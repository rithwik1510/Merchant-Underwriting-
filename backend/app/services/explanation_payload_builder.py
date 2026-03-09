from __future__ import annotations

from app.models import UnderwritingRun


def build_explanation_payload(run: UnderwritingRun) -> dict:
    reason_facts = []
    for reason in run.decision_reasons:
        if reason.reason_type.value in {"hard_stop", "manual_review", "score_component"}:
            reason_facts.append(reason.reason_detail)

    numeric_tokens = _collect_numeric_tokens(run)
    return {
        "merchant_name": run.merchant.merchant_name,
        "category": run.merchant.category,
        "decision": run.decision.value,
        "risk_tier": run.risk_tier.value,
        "credit_offer": {
            "status": run.credit_offer.offer_status.value,
            "final_limit": _fmt(run.credit_offer.final_limit),
            "interest_rate_min": _fmt(run.credit_offer.interest_rate_min),
            "interest_rate_max": _fmt(run.credit_offer.interest_rate_max),
            "tenure_options": run.credit_offer.tenure_options_json,
        },
        "insurance_offer": {
            "status": run.insurance_offer.offer_status.value,
            "coverage_amount": _fmt(run.insurance_offer.coverage_amount),
            "premium_amount": _fmt(run.insurance_offer.premium_amount),
            "premium_rate": _fmt(run.insurance_offer.premium_rate),
            "policy_type": run.insurance_offer.policy_type,
        },
        "key_facts": reason_facts[:6],
        "allowed_numeric_tokens": sorted(numeric_tokens),
        "mode": "operator_explanation",
    }


def build_whatsapp_payload(run: UnderwritingRun, message_type: str) -> dict:
    payload = {
        "merchant_name": run.merchant.merchant_name,
        "decision": run.decision.value,
        "message_type": message_type,
        "mode": "whatsapp_summary",
    }
    if message_type == "credit_offer":
        payload.update(
            {
                "product_name": "GrabCredit",
                "credit_limit": _money_short(run.credit_offer.final_limit),
                "interest_range": _percent_range_text(run.credit_offer.interest_rate_min, run.credit_offer.interest_rate_max),
            }
        )
    elif message_type == "insurance_offer":
        payload.update(
            {
                "product_name": "GrabInsurance",
                "coverage_amount": _money_short(run.insurance_offer.coverage_amount),
                "premium_amount": _money_short(run.insurance_offer.premium_amount),
                "policy_type": run.insurance_offer.policy_type,
            }
        )
    else:
        payload.update(
            {
                "product_name": "GrabCredit and GrabInsurance",
                "credit_limit": _money_short(run.credit_offer.final_limit),
                "interest_range": _percent_range_text(run.credit_offer.interest_rate_min, run.credit_offer.interest_rate_max),
                "coverage_amount": _money_short(run.insurance_offer.coverage_amount),
                "premium_amount": _money_short(run.insurance_offer.premium_amount),
                "policy_type": run.insurance_offer.policy_type,
            }
        )
    payload["allowed_numeric_tokens"] = sorted(_collect_numeric_tokens(run, message_type))
    return payload


def _collect_numeric_tokens(run: UnderwritingRun, message_type: str | None = None) -> set[str]:
    shared_values = {
        "1",
        "2",
        "3",
        "6",
        "9",
        "14",
        "16",
        _fmt(run.numeric_score),
        _fmt(run.merchant.customer_return_rate),
        _fmt(run.merchant.return_and_refund_rate),
        _fmt(run.merchant.avg_order_value),
        _fmt(run.merchant.coupon_redemption_rate),
        _fmt(run.merchant.seasonality_index),
        _fmt(run.feature_snapshot.avg_monthly_gmv_3m),
        _fmt(run.feature_snapshot.annual_gmv_12m),
        _fmt(run.feature_snapshot.gmv_growth_3m_pct),
        _fmt(run.feature_snapshot.gmv_growth_12m_pct),
        _fmt(run.feature_snapshot.gmv_volatility_cv),
        _fmt(run.feature_snapshot.refund_delta_vs_category),
        _fmt(run.feature_snapshot.return_rate_delta_vs_category),
    }
    credit_values = {
        _fmt(run.credit_offer.final_limit),
        _fmt(run.credit_offer.base_limit),
        _fmt(run.credit_offer.interest_rate_min),
        _fmt(run.credit_offer.interest_rate_max),
        _money_numeric_token(run.credit_offer.final_limit),
    }
    insurance_values = {
        _fmt(run.insurance_offer.coverage_amount),
        _fmt(run.insurance_offer.coverage_base),
        _fmt(run.insurance_offer.premium_rate),
        _fmt(run.insurance_offer.premium_amount),
        _money_numeric_token(run.insurance_offer.coverage_amount),
        _money_numeric_token(run.insurance_offer.premium_amount),
    }
    values = set(shared_values)
    if message_type == "credit_offer":
        values.update(credit_values)
    elif message_type == "insurance_offer":
        values.update(insurance_values)
    else:
        values.update(credit_values)
        values.update(insurance_values)
    return {value for value in values if value}


def _fmt(value) -> str | None:
    if value is None:
        return None
    return format(value, "f").rstrip("0").rstrip(".")


def _range_text(min_value, max_value) -> str | None:
    if min_value is None or max_value is None:
        return None
    return f"{_fmt(min_value)}-{_fmt(max_value)}"


def _percent_range_text(min_value, max_value) -> str | None:
    if min_value is None or max_value is None:
        return None
    return f"{_fmt(min_value)}%-{_fmt(max_value)}%"


def _money_short(value) -> str | None:
    if value is None:
        return None
    amount = float(value)
    if amount >= 10000000:
        return f"Rs {_trim_float(amount / 10000000)}Cr"
    if amount >= 100000:
        return f"Rs {_trim_float(amount / 100000)}L"
    if amount >= 1000:
        return f"Rs {_trim_float(amount / 1000)}K"
    return f"Rs {_trim_float(amount)}"


def _money_numeric_token(value) -> str | None:
    if value is None:
        return None
    amount = float(value)
    if amount >= 10000000:
        return _trim_float(amount / 10000000)
    if amount >= 100000:
        return _trim_float(amount / 100000)
    if amount >= 1000:
        return _trim_float(amount / 1000)
    return _trim_float(amount)


def _trim_float(value: float) -> str:
    text = f"{value:.1f}"
    return text.rstrip("0").rstrip(".")
