from types import SimpleNamespace

from sqlalchemy import select

from app.models import UnderwritingRun
from app.services.explanation_payload_builder import build_whatsapp_payload
from app.services.lmstudio_provider import LMStudioProvider


def _create_run(client) -> int:
    client.post("/api/seed/init")
    response = client.post("/api/underwriting/run/m_freshbasket")
    return response.json()["run_id"]


def test_explanation_generation_persists_success(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_explanation",
        lambda self, payload: {
            "summary": "FreshBasket Grocers is approved at Tier 1.",
            "rationale_sentences": [
                "FreshBasket Grocers shows strong and stable merchant performance.",
                "Its GMV growth of 29.8% shows sustained business momentum.",
                "Its customer return rate of 78% is stronger than the category benchmark of 70%.",
                "Its refund and return rate of 1.8% remains below the category benchmark of 2.8%.",
            ],
            "key_strengths": ["Stable GMV trend", "Low refund pressure"],
            "key_risks": [],
            "cited_metrics": [
                {"label": "GMV growth (12M)", "value": "29.8%", "comparison_text": "year-over-year GMV trend"},
                {"label": "Customer return rate", "value": "78%", "benchmark_value": "70%"},
                {"label": "Refund / return rate", "value": "1.8%", "benchmark_value": "2.8%"},
            ],
        },
    )

    response = client.post(f"/api/underwriting/runs/{run_id}/explanation")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["generation_type"] == "decision_explanation"
    assert "summary" in body["output_payload_json"]
    assert len(body["output_payload_json"]["rationale_sentences"]) == 4


def test_explanation_generation_falls_back_on_validation_failure(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_explanation",
        lambda self, payload: {
            "summary": "FreshBasket Grocers is approved with 999999 extra number.",
            "rationale_sentences": ["This adds 999999 which is not allowed."],
            "key_strengths": ["Invented 999999"],
            "key_risks": [],
            "cited_metrics": [],
        },
    )

    response = client.post(f"/api/underwriting/runs/{run_id}/explanation")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "fallback"
    assert body["provider_name"] == "template_fallback"
    assert body["validation_errors_json"]
    assert 3 <= len(body["output_payload_json"]["rationale_sentences"]) <= 5


def test_send_whatsapp_and_status_callback(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_whatsapp_message",
        lambda self, payload: {
            "message_body": "FreshBasket Grocers, you are pre-approved under GrabCredit.",
            "cta_text": "Reply to connect",
            "tone_label": "professional",
        },
    )

    monkeypatch.setattr(
        "app.services.notification_service.get_settings",
        lambda: SimpleNamespace(
            twilio_account_sid="AC123",
            twilio_auth_token="secret",
            twilio_whatsapp_from="whatsapp:+14155238886",
            app_base_url="http://localhost:8000",
        ),
    )

    class FakeResponse:
        is_success = True
        status_code = 201
        text = ""

        def json(self):
            return {"sid": "SM123", "status": "queued"}

    class FakeHttpxClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr("app.services.notification_service.httpx.Client", FakeHttpxClient)

    send_response = client.post(
        f"/api/underwriting/runs/{run_id}/send-whatsapp",
        json={"message_type": "combined_offer"},
    )
    assert send_response.status_code == 200
    send_body = send_response.json()
    assert send_body["delivery_status"] == "queued"
    assert send_body["twilio_message_sid"] == "SM123"
    assert send_body["recipient_phone"].startswith("whatsapp:+91")

    webhook_response = client.post(
        "/api/underwriting/webhooks/twilio/status",
        data={"MessageSid": "SM123", "MessageStatus": "delivered"},
    )
    assert webhook_response.status_code == 200

    communications = client.get(f"/api/underwriting/runs/{run_id}/communications")
    assert communications.status_code == 200
    body = communications.json()
    assert body["latest_whatsapp_draft"] is not None
    assert body["whatsapp_messages"][0]["delivery_status"] == "delivered"


def test_whatsapp_payload_is_scoped_by_message_type(client, db_session) -> None:
    run_id = _create_run(client)
    run = db_session.scalar(select(UnderwritingRun).where(UnderwritingRun.id == run_id))

    credit_payload = build_whatsapp_payload(run, "credit_offer")
    assert credit_payload["message_type"] == "credit_offer"
    assert "credit_limit" in credit_payload
    assert "interest_range" in credit_payload
    assert "coverage_amount" not in credit_payload
    assert "premium_amount" not in credit_payload
    assert credit_payload["credit_limit"].endswith("L")
    assert "%" in credit_payload["interest_range"]
    assert "risk_tier" not in credit_payload

    insurance_payload = build_whatsapp_payload(run, "insurance_offer")
    assert insurance_payload["message_type"] == "insurance_offer"
    assert "coverage_amount" in insurance_payload
    assert "premium_amount" in insurance_payload
    assert "credit_limit" not in insurance_payload
    assert "interest_range" not in insurance_payload
    assert insurance_payload["coverage_amount"].endswith("L")
    assert insurance_payload["premium_amount"].endswith("K")
    assert "risk_tier" not in insurance_payload


def test_credit_whatsapp_generation_falls_back_if_insurance_numbers_leak(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_whatsapp_message",
        lambda self, payload: {
            "message_body": (
                f"{payload['merchant_name']}, credit up to {payload.get('credit_limit')} and coverage up to 4949333.333333."
            ),
            "cta_text": "Reply to connect",
            "tone_label": "professional",
        },
    )

    response = client.post(
        f"/api/underwriting/runs/{run_id}/whatsapp-draft",
        json={"message_type": "credit_offer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "fallback"
    assert body["provider_name"] == "template_fallback"
    assert "coverage" not in body["output_payload_json"]["message_body"].lower()


def test_template_messages_use_compact_merchant_facing_money(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_whatsapp_message",
        lambda self, payload: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    credit_response = client.post(
        f"/api/underwriting/runs/{run_id}/whatsapp-draft",
        json={"message_type": "credit_offer"},
    )
    assert credit_response.status_code == 200
    credit_body = credit_response.json()["output_payload_json"]["message_body"]
    assert "Rs " in credit_body
    assert "L" in credit_body
    assert "tier" not in credit_body.lower()

    insurance_response = client.post(
        f"/api/underwriting/runs/{run_id}/whatsapp-draft",
        json={"message_type": "insurance_offer"},
    )
    assert insurance_response.status_code == 200
    insurance_body = insurance_response.json()["output_payload_json"]["message_body"]
    assert "K" in insurance_body or "L" in insurance_body
    assert "tier" not in insurance_body.lower()


def test_explanation_generation_falls_back_if_rationale_shape_is_too_short(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_explanation",
        lambda self, payload: {
            "summary": "FreshBasket Grocers is approved.",
            "rationale_sentences": ["Too short."],
            "key_strengths": ["Stable GMV trend"],
            "key_risks": [],
            "cited_metrics": [{"label": "GMV growth (12M)", "value": "29.8%"}],
        },
    )

    response = client.post(f"/api/underwriting/runs/{run_id}/explanation")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "fallback"
    assert 3 <= len(body["output_payload_json"]["rationale_sentences"]) <= 5
