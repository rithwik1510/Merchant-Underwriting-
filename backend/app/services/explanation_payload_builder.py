from __future__ import annotations

from decimal import Decimal

from app.models import UnderwritingRun


def build_explanation_payload(run: UnderwritingRun) -> dict:
    reason_facts = []
    for reason in run.decision_reasons:
        if reason.reason_type.value in {"hard_stop", "manual_review", "score_component"}:
            reason_facts.append(reason.reason_detail)

    category_refund_rate = None
    if run.feature_snapshot.refund_delta_vs_category is not None:
        category_refund_rate = Decimal(run.merchant.return_and_refund_rate) - Decimal(run.feature_snapshot.refund_delta_vs_category)

    category_return_rate = None
    if run.feature_snapshot.return_rate_delta_vs_category is not None:
        category_return_rate = Decimal(run.merchant.customer_return_rate) - Decimal(run.feature_snapshot.return_rate_delta_vs_category)

    avg_refund_rate_3m = None
    if getattr(run.merchant, "monthly_metrics", None):
        last_3_metrics = run.merchant.monthly_metrics[-3:]
        if last_3_metrics:
            avg_refund_rate_3m = sum(Decimal(metric.refund_rate) for metric in last_3_metrics) / Decimal(len(last_3_metrics))

    cited_metrics = _build_cited_metrics(run, category_refund_rate, category_return_rate, avg_refund_rate_3m)
    numeric_tokens = _collect_numeric_tokens(run)
    for metric in cited_metrics:
        numeric_tokens.update(_extract_numeric_tokens(metric.get("value")))
        numeric_tokens.update(_extract_numeric_tokens(metric.get("benchmark_value")))
        numeric_tokens.update(_extract_numeric_tokens(metric.get("comparison_text")))
    return {
        "merchant_name": run.merchant.merchant_name,
        "category": run.merchant.category,
        "decision": run.decision.value,
        "risk_tier": run.risk_tier.value,
        "offer_summary": _build_offer_summary(run),
        "merchant_metrics": {
            "avg_monthly_gmv_3m": _fmt(run.feature_snapshot.avg_monthly_gmv_3m),
            "gmv_growth_12m_pct": _fmt(run.feature_snapshot.gmv_growth_12m_pct),
            "customer_return_rate": _fmt(run.merchant.customer_return_rate),
            "return_and_refund_rate": _fmt(run.merchant.return_and_refund_rate),
            "avg_refund_rate_3m": _fmt(avg_refund_rate_3m),
            "seasonality_index": _fmt(run.merchant.seasonality_index),
        },
        "benchmark_metrics": {
            "category_refund_rate": _fmt(category_refund_rate),
            "category_customer_return_rate": _fmt(category_return_rate),
            "refund_delta_vs_category": _fmt(run.feature_snapshot.refund_delta_vs_category),
            "return_rate_delta_vs_category": _fmt(run.feature_snapshot.return_rate_delta_vs_category),
        },
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
        "cited_metrics": cited_metrics,
        "allowed_numeric_tokens": sorted(numeric_tokens),
        "mode": "operator_explanation",
    }


def build_whatsapp_payload(run: UnderwritingRun, message_type: str) -> dict:
    category_refund_rate = None
    if run.feature_snapshot.refund_delta_vs_category is not None:
        category_refund_rate = Decimal(run.merchant.return_and_refund_rate) - Decimal(run.feature_snapshot.refund_delta_vs_category)

    category_return_rate = None
    if run.feature_snapshot.return_rate_delta_vs_category is not None:
        category_return_rate = Decimal(run.merchant.customer_return_rate) - Decimal(run.feature_snapshot.return_rate_delta_vs_category)

    payload = {
        "merchant_name": run.merchant.merchant_name,
        "decision": run.decision.value,
        "risk_tier": run.risk_tier.value,
        "category": run.merchant.category,
        "message_type": message_type,
        "mode": "whatsapp_summary",
        "gmv_growth_12m_pct": f"{_fmt(run.feature_snapshot.gmv_growth_12m_pct)}%" if run.feature_snapshot.gmv_growth_12m_pct is not None else None,
        "customer_return_rate": f"{_fmt(run.merchant.customer_return_rate)}%",
        "category_customer_return_rate": f"{_fmt(category_return_rate)}%" if category_return_rate is not None else None,
        "customer_return_comparison_text": _benchmark_comparison_text(
            Decimal(run.merchant.customer_return_rate),
            category_return_rate,
            positive_when="higher",
        ),
        "refund_rate": f"{_fmt(run.merchant.return_and_refund_rate)}%",
        "category_refund_rate": f"{_fmt(category_refund_rate)}%" if category_refund_rate is not None else None,
        "refund_comparison_text": _benchmark_comparison_text(
            Decimal(run.merchant.return_and_refund_rate),
            category_refund_rate,
            positive_when="lower",
        ),
        "avg_monthly_gmv_3m": _money_short(run.feature_snapshot.avg_monthly_gmv_3m),
    }
    if message_type == "credit_offer":
        payload.update(
            {
                "product_name": "GrabCredit",
                "credit_limit": _money_short(run.credit_offer.final_limit),
                "interest_range": _percent_range_text(run.credit_offer.interest_rate_min, run.credit_offer.interest_rate_max),
                "tenure_options_text": _tenure_text(run.credit_offer.tenure_options_json),
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
                "tenure_options_text": _tenure_text(run.credit_offer.tenure_options_json),
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
        "12",
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
        _money_numeric_token(run.feature_snapshot.avg_monthly_gmv_3m),
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
    if run.feature_snapshot.refund_delta_vs_category is not None:
        values.add(_fmt(Decimal(run.merchant.return_and_refund_rate) - Decimal(run.feature_snapshot.refund_delta_vs_category)))
    if run.feature_snapshot.return_rate_delta_vs_category is not None:
        values.add(_fmt(Decimal(run.merchant.customer_return_rate) - Decimal(run.feature_snapshot.return_rate_delta_vs_category)))
    if message_type == "credit_offer":
        values.update(credit_values)
    elif message_type == "insurance_offer":
        values.update(insurance_values)
    else:
        values.update(credit_values)
        values.update(insurance_values)
    expanded_values: set[str] = set()
    for value in values:
        if not value:
            continue
        expanded_values.update(_numeric_variants(value))
    return expanded_values


def _fmt(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        value = value.quantize(Decimal("0.0001"))
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


def _tenure_text(options: list[int] | None) -> str | None:
    if not options:
        return None
    return ", ".join(f"{int(option)} months" for option in options)


def _numeric_variants(value: str) -> set[str]:
    variants = {value}
    try:
        decimal_value = Decimal(value)
    except Exception:
        return variants

    for precision in ("0.1", "0.01", "0.0001"):
        rounded = decimal_value.quantize(Decimal(precision))
        variants.add(format(rounded, "f").rstrip("0").rstrip("."))
    return {variant for variant in variants if variant}


def _extract_numeric_tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    tokens = set()
    current = ""
    for char in value:
        if char.isdigit() or char == ".":
            current += char
            continue
        if current:
            tokens.update(_numeric_variants(current))
            current = ""
    if current:
        tokens.update(_numeric_variants(current))
    return tokens


def _build_offer_summary(run: UnderwritingRun) -> str:
    tier_text = run.risk_tier.value.replace("_", " ").title()
    if run.decision.value == "approved":
        return (
            f"Offer approved at {tier_text} with credit up to {_money_short(run.credit_offer.final_limit)} "
            f"and insurance coverage up to {_money_short(run.insurance_offer.coverage_amount)}."
        )
    if run.decision.value == "manual_review":
        return (
            f"Manual review at {tier_text} with indicative credit up to {_money_short(run.credit_offer.final_limit)} "
            f"and coverage up to {_money_short(run.insurance_offer.coverage_amount)}."
        )
    return f"Offer not approved because the merchant failed core underwriting checks at {tier_text}."


def _benchmark_comparison_text(
    merchant_value: Decimal | None,
    benchmark_value: Decimal | None,
    *,
    positive_when: str,
) -> str | None:
    if merchant_value is None or benchmark_value is None:
        return None

    delta = merchant_value - benchmark_value
    delta_abs = abs(delta)
    if delta_abs == 0:
        return f"in line with the category benchmark of {_fmt(benchmark_value)}%"

    unit = "percentage point" if _fmt(delta_abs) == "1" else "percentage points"

    if positive_when == "higher":
        if delta > 0:
            return f"{_fmt(delta_abs)} {unit} above the category benchmark of {_fmt(benchmark_value)}%"
        return f"{_fmt(delta_abs)} {unit} below the category benchmark of {_fmt(benchmark_value)}%"

    if delta < 0:
        return f"{_fmt(delta_abs)} {unit} below the category benchmark of {_fmt(benchmark_value)}%"
    return f"{_fmt(delta_abs)} {unit} above the category benchmark of {_fmt(benchmark_value)}%"


def _build_cited_metrics(
    run: UnderwritingRun,
    category_refund_rate: Decimal | None,
    category_return_rate: Decimal | None,
    avg_refund_rate_3m: Decimal | None,
) -> list[dict[str, str]]:
    cited = []
    if run.feature_snapshot.gmv_growth_12m_pct is not None:
        cited.append(
            {
                "label": "GMV growth (12M)",
                "value": f"{_fmt(run.feature_snapshot.gmv_growth_12m_pct)}%",
                "comparison_text": "year-over-year GMV trend",
            }
        )
    cited.append(
        {
            "label": "Customer return rate",
            "value": f"{_fmt(run.merchant.customer_return_rate)}%",
            "benchmark_value": f"{_fmt(category_return_rate)}%" if category_return_rate is not None else "",
            "comparison_text": _benchmark_comparison_text(
                Decimal(run.merchant.customer_return_rate),
                category_return_rate,
                positive_when="higher",
            )
            or "repeat demand relative to category",
        }
    )
    refund_value = avg_refund_rate_3m if avg_refund_rate_3m is not None else Decimal(run.merchant.return_and_refund_rate)
    cited.append(
        {
            "label": "Refund / return rate",
            "value": f"{_fmt(refund_value)}%",
            "benchmark_value": f"{_fmt(category_refund_rate)}%" if category_refund_rate is not None else "",
            "comparison_text": _benchmark_comparison_text(
                refund_value,
                category_refund_rate,
                positive_when="lower",
            )
            or "merchant pressure versus category benchmark",
        }
    )
    if run.feature_snapshot.avg_monthly_gmv_3m is not None:
        cited.append(
            {
                "label": "Average monthly GMV (3M)",
                "value": _money_short(run.feature_snapshot.avg_monthly_gmv_3m) or "",
                "comparison_text": "recent business scale",
            }
        )
    return cited
