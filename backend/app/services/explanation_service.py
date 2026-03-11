from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import LLMGeneration, LLMGenerationStatus, LLMGenerationType, UnderwritingRun
from app.schemas import CommunicationsResponse, ExplanationContentResponse, WhatsAppMessageResponse
from app.services.explanation_payload_builder import build_explanation_payload, build_whatsapp_payload
from app.services.lmstudio_provider import LMStudioProvider
from app.services.template_provider import TemplateProvider
from app.services.validation_service import validate_generation_output


def generate_run_explanation(db: Session, run_id: int) -> ExplanationContentResponse:
    run = _load_run(db, run_id)
    payload = build_explanation_payload(run)
    generation = _generate_with_fallback(db, run_id, payload, LLMGenerationType.DECISION_EXPLANATION)
    db.commit()
    return _map_generation(generation)


def generate_run_whatsapp_message(db: Session, run_id: int, message_type: str) -> ExplanationContentResponse:
    run = _load_run(db, run_id)
    payload = build_whatsapp_payload(run, message_type)
    generation = _generate_with_fallback(db, run_id, payload, LLMGenerationType.WHATSAPP_MESSAGE)
    db.commit()
    return _map_generation(generation)


def get_run_communications(db: Session, run_id: int) -> CommunicationsResponse:
    run = _load_run(db, run_id)
    explanations = [generation for generation in run.llm_generations if generation.generation_type == LLMGenerationType.DECISION_EXPLANATION]
    drafts = [generation for generation in run.llm_generations if generation.generation_type == LLMGenerationType.WHATSAPP_MESSAGE]

    return CommunicationsResponse(
        latest_explanation=_map_generation(explanations[-1]) if explanations else None,
        latest_whatsapp_draft=_map_generation(drafts[-1]) if drafts else None,
        whatsapp_messages=[
            WhatsAppMessageResponse(
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
            for message in run.whatsapp_messages
        ],
    )


def _load_run(db: Session, run_id: int) -> UnderwritingRun:
    run = db.scalar(
        select(UnderwritingRun)
        .options(
            selectinload(UnderwritingRun.merchant),
            selectinload(UnderwritingRun.feature_snapshot),
            selectinload(UnderwritingRun.credit_offer),
            selectinload(UnderwritingRun.insurance_offer),
            selectinload(UnderwritingRun.decision_reasons),
            selectinload(UnderwritingRun.llm_generations),
            selectinload(UnderwritingRun.whatsapp_messages),
        )
        .where(UnderwritingRun.id == run_id)
    )
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")
    return run


def _generate_with_fallback(db: Session, run_id: int, payload: dict, generation_type: LLMGenerationType) -> LLMGeneration:
    settings = get_settings()
    primary = LMStudioProvider() if settings.llm_provider == "lmstudio" else TemplateProvider()
    fallback = TemplateProvider()

    try:
        output = _call_provider(primary, payload, generation_type)
        errors = validate_generation_output(payload, output, generation_type.value)
        if errors:
            _persist_generation(
                db,
                run_id,
                primary.provider_name,
                primary.model_name,
                generation_type,
                LLMGenerationStatus.FAILED_VALIDATION,
                payload,
                output,
                errors,
            )
            fallback_output = _call_provider(fallback, payload, generation_type)
            return _persist_generation(
                db,
                run_id,
                fallback.provider_name,
                fallback.model_name,
                generation_type,
                LLMGenerationStatus.FALLBACK,
                payload,
                fallback_output,
                errors,
            )
        return _persist_generation(
            db,
            run_id,
            primary.provider_name,
            primary.model_name,
            generation_type,
            LLMGenerationStatus.SUCCESS,
            payload,
            output,
            None,
        )
    except Exception as exc:
        fallback_output = _call_provider(fallback, payload, generation_type)
        return _persist_generation(
            db,
            run_id,
            fallback.provider_name,
            fallback.model_name,
            generation_type,
            LLMGenerationStatus.FALLBACK,
            payload,
            fallback_output,
            [str(exc)],
        )


def _call_provider(provider, payload: dict, generation_type: LLMGenerationType) -> dict:
    if generation_type == LLMGenerationType.DECISION_EXPLANATION:
        return provider.generate_explanation(payload)
    return provider.generate_whatsapp_message(payload)


def _persist_generation(
    db: Session,
    run_id: int,
    provider_name: str,
    model_name: str,
    generation_type: LLMGenerationType,
    status: LLMGenerationStatus,
    input_payload: dict,
    output_payload: dict,
    validation_errors: list[str] | None,
) -> LLMGeneration:
    generation = LLMGeneration(
        underwriting_run_id=run_id,
        provider_name=provider_name,
        model_name=model_name,
        generation_type=generation_type,
        status=status,
        input_payload_json=input_payload,
        output_payload_json=output_payload,
        validation_errors_json=validation_errors,
    )
    db.add(generation)
    db.flush()
    return generation


def _map_generation(generation: LLMGeneration) -> ExplanationContentResponse:
    return ExplanationContentResponse(
        generation_id=generation.id,
        provider_name=generation.provider_name,
        model_name=generation.model_name,
        generation_type=generation.generation_type.value,
        status=generation.status.value,
        output_payload_json=generation.output_payload_json,
        validation_errors_json=generation.validation_errors_json,
        created_at=generation.created_at,
    )
