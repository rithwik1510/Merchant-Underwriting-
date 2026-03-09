from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import CommunicationsResponse, ExplanationContentResponse, WhatsAppDraftRequest, WhatsAppMessageResponse, WhatsAppSendRequest
from app.services.explanation_service import generate_run_explanation, generate_run_whatsapp_message, get_run_communications
from app.services.notification_service import send_whatsapp_for_run, update_whatsapp_status


router = APIRouter()


@router.post("/runs/{run_id}/explanation", response_model=ExplanationContentResponse)
def create_explanation(run_id: int, db: Session = Depends(get_db)) -> ExplanationContentResponse:
    return generate_run_explanation(db, run_id)


@router.post("/runs/{run_id}/whatsapp-draft", response_model=ExplanationContentResponse)
def create_whatsapp_draft(
    run_id: int,
    request: WhatsAppDraftRequest,
    db: Session = Depends(get_db),
) -> ExplanationContentResponse:
    return generate_run_whatsapp_message(db, run_id, request.message_type)


@router.post("/runs/{run_id}/send-whatsapp", response_model=WhatsAppMessageResponse)
def send_whatsapp(
    run_id: int,
    request: WhatsAppSendRequest,
    db: Session = Depends(get_db),
) -> WhatsAppMessageResponse:
    return send_whatsapp_for_run(db, run_id, request.recipient_phone, request.message_type)


@router.post("/webhooks/twilio/status")
async def twilio_status_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    form = await request.form()
    update_whatsapp_status(db, dict(form))
    return {"status": "ok"}


@router.get("/runs/{run_id}/communications", response_model=CommunicationsResponse)
def get_communications(run_id: int, db: Session = Depends(get_db)) -> CommunicationsResponse:
    return get_run_communications(db, run_id)
