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
                "We are offering credit up to Rs 46.5L and insurance coverage up to 49.5L because the finalized underwriting signals support this offer.",
                "Your GMV has grown 29.8% over the last 12 months, which shows sustained business momentum.",
                "Your customer return rate of 78% is above the category benchmark of 70%, which indicates repeat demand stability.",
                "Your refund rate of 1.8% is below the category benchmark of 2.8%, which supports the approved risk posture.",
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
            "message_body": (
                "GrabOn update for FreshBasket Grocers: your pre-approved GrabCredit and GrabInsurance offer is ready. "
                "You are eligible for working capital up to Rs 46.5L and insurance coverage up to Rs 49.5L. "
                "This reflects 29.8% year-over-year GMV growth on GrabOn. "
                "Please review and accept the offer in your merchant dashboard."
            ),
            "cta_text": "Review offer",
            "tone_label": "business_notification",
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
    assert credit_payload["risk_tier"].startswith("tier_")
    assert "gmv_growth_12m_pct" in credit_payload
    assert "tenure_options_text" in credit_payload

    insurance_payload = build_whatsapp_payload(run, "insurance_offer")
    assert insurance_payload["message_type"] == "insurance_offer"
    assert "coverage_amount" in insurance_payload
    assert "premium_amount" in insurance_payload
    assert "credit_limit" not in insurance_payload
    assert "interest_range" not in insurance_payload
    assert insurance_payload["coverage_amount"].endswith("L")
    assert insurance_payload["premium_amount"].endswith("K")
    assert insurance_payload["risk_tier"].startswith("tier_")


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
    assert "pre-approved" in insurance_body.lower() or "under final review" in insurance_body.lower()
    assert "dashboard" in insurance_body.lower() or "final outcome" in insurance_body.lower()


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


def test_lmstudio_provider_strips_think_blocks_before_json_parse() -> None:
    content = """
    <think>
    hidden reasoning
    </think>
    ```json
    {"summary":"ok","rationale_sentences":["a","b","c"],"key_strengths":[],"key_risks":[],"cited_metrics":[]}
    ```
    """

    parsed = LMStudioProvider._parse_json_content(content)

    assert parsed["summary"] == "ok"
    assert len(parsed["rationale_sentences"]) == 3


def test_lmstudio_provider_uses_single_compatible_request_shape(monkeypatch) -> None:
    captured = {}

    monkeypatch.setattr(
        "app.services.lmstudio_provider.get_settings",
        lambda: SimpleNamespace(
            lmstudio_base_url="http://127.0.0.1:1234",
            lmstudio_model="qwen/qwen3-8b",
        ),
    )

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"summary":"ok","rationale_sentences":["one","two","three"],'
                                '"key_strengths":[],"key_risks":[],"cited_metrics":[]}'
                            )
                        }
                    }
                ]
            }

    class FakeHttpxClient:
        def __init__(self, *args, **kwargs):
            captured["timeout"] = kwargs.get("timeout")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json):
            captured["url"] = url
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.lmstudio_provider.httpx.Client", FakeHttpxClient)

    provider = LMStudioProvider()
    output = provider.generate_explanation({"merchant_name": "FoodDash", "allowed_numeric_tokens": []})

    assert output["summary"] == "ok"
    assert captured["url"] == "http://127.0.0.1:1234/v1/chat/completions"
    assert "response_format" not in captured["json"]
    assert captured["json"]["max_tokens"] == 700
    assert "/no_think" in captured["json"]["messages"][0]["content"]


def test_explanation_accepts_grounded_rounded_numeric_variants(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_explanation",
        lambda self, payload: {
                "summary": "FreshBasket Grocers is approved at Tier 1.",
                "rationale_sentences": [
                    "We are offering credit up to Rs 46.5L and insurance coverage up to Rs 49.5L because the finalized underwriting signals support this offer.",
                    "Your GMV has grown 29.8% over the last 12 months, which supports business momentum.",
                    "Your customer return rate is 78% versus a category benchmark of 70%, which signals repeat demand quality.",
                    "Your refund and return pressure is 1.87% against a category benchmark of 2.8%, which directly informs the offer risk posture.",
                ],
                "key_strengths": ["Stable GMV trend", "Low refund pressure"],
                "key_risks": [],
                "cited_metrics": [
                    {"label": "Average monthly GMV (3M)", "value": "Rs 30.9L", "comparison_text": "recent business scale"},
                ],
            },
        )

    response = client.post(f"/api/underwriting/runs/{run_id}/explanation")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["provider_name"] == "lmstudio"


def test_whatsapp_generation_persists_business_notification_style(client, monkeypatch) -> None:
    run_id = _create_run(client)

    monkeypatch.setattr(
        LMStudioProvider,
        "generate_whatsapp_message",
        lambda self, payload: {
            "message_body": (
                "GrabOn update for FreshBasket Grocers: your pre-approved GrabCredit offer is ready. "
                "You are eligible for working capital up to Rs 46.5L at 14%-16% with tenure options of 3 months, 6 months, 12 months. "
                "This reflects 29.8% year-over-year GMV growth on GrabOn. "
                "Please review and accept the offer in your merchant dashboard."
            ),
            "cta_text": "Review offer",
            "tone_label": "business_notification",
        },
    )

    response = client.post(
        f"/api/underwriting/runs/{run_id}/whatsapp-draft",
        json={"message_type": "credit_offer"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["provider_name"] == "lmstudio"
    assert "pre-approved" in body["output_payload_json"]["message_body"].lower()
    assert "dashboard" in body["output_payload_json"]["message_body"].lower()


def test_lmstudio_whatsapp_output_is_normalized_to_dashboard_notification() -> None:
    payload = {
        "merchant_name": "FoodDash Express",
        "product_name": "GrabCredit",
        "decision": "approved",
    }
    output = {
        "message_body": "Your offer for GrabCredit is ready.",
        "cta_text": "",
        "tone_label": "",
    }

    normalized = LMStudioProvider._normalize_whatsapp_output(payload, output)

    assert "FoodDash Express" in normalized["message_body"]
    assert "pre-approved" in normalized["message_body"].lower()
    assert "dashboard" in normalized["message_body"].lower()
    assert normalized["cta_text"] == "Review offer"
    assert normalized["tone_label"] == "business_notification"


def test_lmstudio_explanation_output_is_normalized_to_offer_because_style() -> None:
    payload = {
        "decision": "approved",
        "risk_tier": "tier_2",
        "credit_offer": {"final_limit": "2050000"},
        "insurance_offer": {"coverage_amount": "3109333.33"},
        "merchant_metrics": {
            "gmv_growth_12m_pct": "25.95",
            "customer_return_rate": "69",
            "avg_refund_rate_3m": "3.0333",
            "return_and_refund_rate": "2.9",
        },
        "benchmark_metrics": {
            "category_customer_return_rate": "70",
            "category_refund_rate": "2.8",
        },
    }
    output = {
        "summary": "FoodDash Express has been approved.",
        "rationale_sentences": [
            "FoodDash Express has been approved for a Tier 2 offer.",
            "Other sentence.",
            "Another sentence.",
            "Final sentence.",
        ],
        "key_strengths": [],
        "key_risks": [],
        "cited_metrics": [],
    }

    normalized = LMStudioProvider._normalize_explanation_output(payload, output)

    assert normalized["rationale_sentences"][0].startswith("We are offering")
    assert "because" in normalized["rationale_sentences"][0].lower()
    assert "GMV has grown 25.95% YoY" in normalized["rationale_sentences"][0]
