from types import SimpleNamespace

from app.models import LLMGeneration, LLMGenerationType
from app.services.lmstudio_provider import LMStudioProvider


def _create_run(client, merchant_id: str = "m_freshbasket") -> int:
    client.post("/api/seed/init")
    response = client.post(f"/api/underwriting/run/{merchant_id}")
    return response.json()["run_id"]


def test_health_endpoint_reports_ok(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejected_run_cannot_receive_whatsapp(client) -> None:
    run_id = _create_run(client, "m_quickbyte")

    response = client.post(
        f"/api/underwriting/runs/{run_id}/send-whatsapp",
        json={"recipient_phone": "whatsapp:+919999999999", "message_type": "combined_offer"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Rejected merchants cannot receive outbound WhatsApp in Phase 3"


def test_send_whatsapp_marks_message_failed_when_twilio_is_unconfigured(client, monkeypatch) -> None:
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
            twilio_account_sid=None,
            twilio_auth_token=None,
            twilio_whatsapp_from=None,
            app_base_url="http://localhost:8000",
        ),
    )

    response = client.post(
        f"/api/underwriting/runs/{run_id}/send-whatsapp",
        json={"recipient_phone": "whatsapp:+919999999999", "message_type": "combined_offer"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["delivery_status"] == "failed"
    assert body["failure_reason"] == "Twilio credentials not configured"


def test_send_whatsapp_uses_mounted_status_callback_route(client, db_session, monkeypatch) -> None:
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

    captured_request = {}

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

        def post(self, url, headers=None, data=None):
            captured_request["url"] = url
            captured_request["data"] = data
            return FakeResponse()

    monkeypatch.setattr("app.services.notification_service.httpx.Client", FakeHttpxClient)

    response = client.post(
        f"/api/underwriting/runs/{run_id}/send-whatsapp",
        json={"recipient_phone": "whatsapp:+919999999999", "message_type": "combined_offer"},
    )

    assert response.status_code == 200
    assert captured_request["data"]["StatusCallback"] == "http://localhost:8000/api/underwriting/webhooks/twilio/status"

    whatsapp_generation = db_session.query(LLMGeneration).filter(
        LLMGeneration.underwriting_run_id == run_id,
        LLMGeneration.generation_type == LLMGenerationType.WHATSAPP_MESSAGE,
    ).all()
    assert len(whatsapp_generation) == 1


def test_mandate_start_is_idempotent_and_preserves_original_session_data(client) -> None:
    run_id = _create_run(client, "m_freshbasket")
    client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "combined",
            "accepted_by_name": "Amit Sharma",
            "accepted_phone": "919999999999",
            "accepted_via": "dashboard",
        },
    )

    first = client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Amit Sharma", "mobile_number": "919999999999"},
    )
    second = client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Changed Name", "mobile_number": "918888888888"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["account_holder_name"] == "Amit Sharma"
    assert second.json()["mobile_number_masked"].endswith("99")


def test_mandate_enforces_step_order(client) -> None:
    run_id = _create_run(client, "m_freshbasket")
    client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "combined",
            "accepted_by_name": "Amit Sharma",
            "accepted_phone": "919999999999",
            "accepted_via": "dashboard",
        },
    )
    client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Amit Sharma", "mobile_number": "919999999999"},
    )

    otp_before_bank = client.post(f"/api/mandates/{run_id}/send-otp")
    assert otp_before_bank.status_code == 400
    assert otp_before_bank.json()["detail"] == "OTP can only be sent after bank selection"

    complete_before_bank = client.post(f"/api/mandates/{run_id}/complete")
    assert complete_before_bank.status_code == 400
    assert complete_before_bank.json()["detail"] == "Mandate can only be completed after OTP verification"
