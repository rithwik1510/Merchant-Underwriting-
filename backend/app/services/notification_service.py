from __future__ import annotations

import base64
import json

import httpx
from fastapi import HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import LLMGeneration, LLMGenerationType, UnderwritingRun, WhatsAppDeliveryStatus, WhatsAppMessage, WhatsAppMessageType
from app.schemas import WhatsAppMessageResponse
from app.services.explanation_service import generate_run_whatsapp_message


def send_whatsapp_for_run(db: Session, run_id: int, recipient_phone: str | None, message_type: str) -> WhatsAppMessageResponse:
    run = db.scalar(
        select(UnderwritingRun)
        .options(selectinload(UnderwritingRun.llm_generations))
        .where(UnderwritingRun.id == run_id)
    )
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")
    if run.decision.value == "rejected":
        raise HTTPException(status_code=400, detail="Rejected merchants cannot receive outbound WhatsApp in Phase 3")
    recipient_phone = recipient_phone or run.merchant.registered_whatsapp_number
    if not recipient_phone:
        raise HTTPException(status_code=400, detail="Merchant does not have a registered WhatsApp number")

    draft = generate_run_whatsapp_message(db, run_id, message_type)
    latest_generation = db.scalar(
        select(LLMGeneration)
        .where(
            LLMGeneration.underwriting_run_id == run_id,
            LLMGeneration.generation_type == LLMGenerationType.WHATSAPP_MESSAGE,
        )
        .order_by(desc(LLMGeneration.created_at), desc(LLMGeneration.id))
    )

    message = WhatsAppMessage(
        underwriting_run_id=run_id,
        llm_generation_id=latest_generation.id if latest_generation.generation_type == LLMGenerationType.WHATSAPP_MESSAGE else None,
        recipient_phone=recipient_phone,
        message_type=WhatsAppMessageType(message_type),
        content_text=draft.output_payload_json["message_body"],
        delivery_status=WhatsAppDeliveryStatus.DRAFT,
    )
    db.add(message)
    db.flush()

    settings = get_settings()
    if not settings.twilio_account_sid or not settings.twilio_auth_token or not settings.twilio_whatsapp_from:
        message.failure_reason = "Twilio credentials not configured"
        message.delivery_status = WhatsAppDeliveryStatus.FAILED
        db.commit()
        return _map_message(message)

    auth_header = base64.b64encode(f"{settings.twilio_account_sid}:{settings.twilio_auth_token}".encode()).decode()
    callback_url = f"{settings.app_base_url.rstrip('/')}/api/underwriting/webhooks/twilio/status"
    request_data = {
        "To": recipient_phone,
        "StatusCallback": callback_url,
    }
    twilio_content_sid = getattr(settings, "twilio_content_sid", None)
    twilio_content_variables = getattr(settings, "twilio_content_variables", None)
    if twilio_content_sid:
        request_data["From"] = settings.twilio_whatsapp_from
        request_data["ContentSid"] = twilio_content_sid
        if twilio_content_variables:
            request_data["ContentVariables"] = json.dumps(twilio_content_variables)
    else:
        request_data["From"] = settings.twilio_whatsapp_from
        request_data["Body"] = message.content_text

    with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
        response = client.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json",
            headers={"Authorization": f"Basic {auth_header}"},
            data=request_data,
        )
        if response.is_success:
            payload = response.json()
            message.twilio_message_sid = payload.get("sid")
            message.provider_response_json = payload
            message.delivery_status = WhatsAppDeliveryStatus.QUEUED
        else:
            message.provider_response_json = {"status_code": response.status_code, "body": response.text}
            message.failure_reason = "Twilio send failed"
            message.delivery_status = WhatsAppDeliveryStatus.FAILED
    db.commit()
    return _map_message(message)


def update_whatsapp_status(db: Session, callback_payload: dict) -> None:
    sid = callback_payload.get("MessageSid")
    if not sid:
        return
    message = db.scalar(select(WhatsAppMessage).where(WhatsAppMessage.twilio_message_sid == sid))
    if not message:
        return
    raw_status = (callback_payload.get("MessageStatus") or "").lower()
    status_map = {
        "queued": WhatsAppDeliveryStatus.QUEUED,
        "sent": WhatsAppDeliveryStatus.SENT,
        "delivered": WhatsAppDeliveryStatus.DELIVERED,
        "failed": WhatsAppDeliveryStatus.FAILED,
        "undelivered": WhatsAppDeliveryStatus.FAILED,
    }
    if raw_status in status_map:
        message.delivery_status = status_map[raw_status]
    message.provider_response_json = callback_payload
    db.commit()


def _map_message(message: WhatsAppMessage) -> WhatsAppMessageResponse:
    return WhatsAppMessageResponse(
        id=message.id,
        llm_generation_id=message.llm_generation_id,
        recipient_phone=message.recipient_phone,
        message_type=message.message_type.value,
        content_text=message.content_text,
        twilio_message_sid=message.twilio_message_sid,
        delivery_status=message.delivery_status.value,
        provider_response_json=message.provider_response_json,
        failure_reason=message.failure_reason,
        created_at=message.created_at,
        updated_at=message.updated_at,
    )
