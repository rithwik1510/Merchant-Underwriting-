from __future__ import annotations

import re


NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")
SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def validate_generation_output(payload: dict, output: dict, generation_type: str) -> list[str]:
    errors: list[str] = []
    required_keys = {
        "decision_explanation": {"summary", "rationale_sentences", "key_strengths", "key_risks", "cited_metrics"},
        "whatsapp_message": {"message_body", "cta_text", "tone_label"},
    }[generation_type]

    missing = required_keys - set(output.keys())
    if missing:
        errors.append(f"Missing keys: {', '.join(sorted(missing))}")

    allowed_tokens = set(payload.get("allowed_numeric_tokens", []))
    text_blob = " ".join(_flatten_strings(output))
    found_tokens = set(NUMBER_PATTERN.findall(text_blob))
    if not found_tokens.issubset(allowed_tokens):
        extras = sorted(found_tokens - allowed_tokens)
        errors.append(f"Unexpected numeric tokens: {', '.join(extras)}")

    if generation_type == "decision_explanation":
        rationale_sentences = output.get("rationale_sentences")
        if not isinstance(rationale_sentences, list) or not (3 <= len(rationale_sentences) <= 5):
            errors.append("Explanation must contain between 3 and 5 rationale sentences")
        cited_metrics = output.get("cited_metrics")
        if not isinstance(cited_metrics, list) or not cited_metrics:
            errors.append("Explanation must include cited metrics")
        benchmark_metrics = payload.get("benchmark_metrics", {})
        benchmark_present = bool(
            benchmark_metrics.get("category_refund_rate") or benchmark_metrics.get("category_customer_return_rate")
        )
        if benchmark_present and text_blob.lower().count("benchmark") == 0 and " versus " not in text_blob.lower():
            errors.append("Benchmark-backed explanations must reference category comparison")
        if isinstance(rationale_sentences, list) and rationale_sentences:
            opener = rationale_sentences[0].lower()
            decision = payload.get("decision")
            if decision == "approved" and "we are offering" not in opener:
                errors.append("Approved explanations must start with 'We are offering'")
            if decision == "manual_review" and "we are recommending manual review because" not in opener:
                errors.append("Manual review explanations must start with 'We are recommending manual review because'")
            if decision == "rejected" and "we are unable to offer" not in opener:
                errors.append("Rejected explanations must start with 'We are unable to offer'")
    else:
        message_body = output.get("message_body")
        if not isinstance(message_body, str) or not message_body.strip():
            errors.append("WhatsApp output must include message_body text")
        else:
            sentence_count = len([part for part in SENTENCE_SPLIT_PATTERN.split(message_body.strip()) if part.strip()])
            if not (2 <= sentence_count <= 4):
                errors.append("WhatsApp message must contain between 2 and 4 sentences")
            merchant_name = payload.get("merchant_name", "")
            if merchant_name and merchant_name.lower() not in message_body.lower():
                errors.append("WhatsApp message must mention the merchant name")
            product_name = payload.get("product_name")
            if product_name and product_name.lower() not in message_body.lower():
                errors.append("WhatsApp message must mention the selected product")
            if "pre-approved" not in message_body.lower() and payload.get("decision") == "approved":
                errors.append("Approved WhatsApp messages must state that the offer is pre-approved")
            if "dashboard" not in message_body.lower() and payload.get("decision") in {"approved", "manual_review"}:
                errors.append("WhatsApp messages should direct the merchant back to the dashboard")

    return errors


def _flatten_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_flatten_strings(item))
        return strings
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_flatten_strings(item))
        return strings
    return []
