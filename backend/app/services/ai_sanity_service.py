from __future__ import annotations

from app.core.config import get_settings
from app.models import AISanityCheck, AISanityCheckStatus, UnderwritingRun
from app.services.claude_provider import ClaudeProvider
from app.services.explanation_payload_builder import build_explanation_payload, build_whatsapp_payload
from app.services.lmstudio_provider import LMStudioProvider
from app.services.template_provider import TemplateProvider
from app.services.validation_service import validate_generation_output


def create_ai_sanity_check(run: UnderwritingRun) -> AISanityCheck:
    if run.decision.value == "rejected" and run.hard_stop_triggered:
        payload = _build_payload(run)
        return AISanityCheck(
            underwriting_run_id=run.id,
            provider_name="deterministic_skip",
            model_name="hard_stop_skip",
            status=AISanityCheckStatus.SKIPPED,
            issue_codes_json=[],
            notes_json=["Hard-stop rejection finalized deterministically; AI sanity check skipped."],
            suggested_explanation_focus_json=["Explain the blocking policy checks clearly."],
            suggested_message_focus_json=["Keep merchant messaging concise and factual."],
            input_payload_json=payload,
            output_payload_json={"status": "skipped"},
            validation_errors_json=None,
        )

    payload = _build_payload(run)
    provider = _resolve_provider()
    try:
        output = provider.generate_sanity_check(payload)
        errors = validate_generation_output(payload, output, "sanity_check")
        if errors:
            return AISanityCheck(
                underwriting_run_id=run.id,
                provider_name=provider.provider_name,
                model_name=provider.model_name,
                status=AISanityCheckStatus.UNAVAILABLE,
                issue_codes_json=["invalid_sanity_output"],
                notes_json=["AI sanity check returned invalid structured output; deterministic result was preserved."],
                suggested_explanation_focus_json=[],
                suggested_message_focus_json=[],
                input_payload_json=payload,
                output_payload_json=output,
                validation_errors_json=errors,
            )

        output_status = AISanityCheckStatus.PASSED if output.get("status") == "passed" else AISanityCheckStatus.WARNING
        return AISanityCheck(
            underwriting_run_id=run.id,
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            status=output_status,
            issue_codes_json=output.get("issue_codes", []),
            notes_json=output.get("notes", []),
            suggested_explanation_focus_json=output.get("suggested_explanation_focus", []),
            suggested_message_focus_json=output.get("suggested_message_focus", []),
            input_payload_json=payload,
            output_payload_json=output,
            validation_errors_json=None,
        )
    except Exception as exc:
        return AISanityCheck(
            underwriting_run_id=run.id,
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            status=AISanityCheckStatus.UNAVAILABLE,
            issue_codes_json=["provider_unavailable"],
            notes_json=["AI sanity check was unavailable; deterministic result was preserved."],
            suggested_explanation_focus_json=[],
            suggested_message_focus_json=[],
            input_payload_json=payload,
            output_payload_json={"error": str(exc)},
            validation_errors_json=[str(exc)],
        )


def _build_payload(run: UnderwritingRun) -> dict:
    explanation_payload = build_explanation_payload(run)
    combined_message_payload = build_whatsapp_payload(run, "combined_offer")
    allowed_numeric_tokens = sorted(
        set(explanation_payload.get("allowed_numeric_tokens", []))
        | set(combined_message_payload.get("allowed_numeric_tokens", []))
    )
    return {
        "merchant_name": run.merchant.merchant_name,
        "category": run.merchant.category,
        "decision": run.decision.value,
        "risk_tier": run.risk_tier.value,
        "offer_summary": explanation_payload.get("offer_summary"),
        "merchant_metrics": explanation_payload.get("merchant_metrics", {}),
        "benchmark_metrics": explanation_payload.get("benchmark_metrics", {}),
        "credit_offer": explanation_payload.get("credit_offer", {}),
        "insurance_offer": explanation_payload.get("insurance_offer", {}),
        "key_facts": explanation_payload.get("key_facts", []),
        "cited_metrics": explanation_payload.get("cited_metrics", []),
        "message_preview_context": {
            "product_name": combined_message_payload.get("product_name"),
            "credit_limit": combined_message_payload.get("credit_limit"),
            "coverage_amount": combined_message_payload.get("coverage_amount"),
            "premium_amount": combined_message_payload.get("premium_amount"),
            "interest_range": combined_message_payload.get("interest_range"),
            "tenure_options_text": combined_message_payload.get("tenure_options_text"),
            "refund_comparison_text": combined_message_payload.get("refund_comparison_text"),
            "customer_return_comparison_text": combined_message_payload.get("customer_return_comparison_text"),
        },
        "allowed_numeric_tokens": allowed_numeric_tokens,
        "mode": "qa_sanity_check",
    }


def _resolve_provider():
    settings = get_settings()
    if settings.llm_provider == "claude":
        return ClaudeProvider()
    if settings.llm_provider == "lmstudio":
        return LMStudioProvider()
    return TemplateProvider()
