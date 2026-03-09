from __future__ import annotations

from decimal import Decimal

from app.models import Merchant
from app.services.underwriting_math import quantize_2, round_to_nearest
from app.services.underwriting_types import CreditOfferResult, FeatureResult, InsuranceOfferResult, ReasonData, ScorecardResult


def build_credit_offer(
    features: FeatureResult,
    score_result: ScorecardResult,
    decision: str,
) -> CreditOfferResult:
    if decision == "rejected":
        return CreditOfferResult(None, None, None, None, [], "not_offered", [])

    if features.avg_monthly_gmv_3m is None:
        return CreditOfferResult(None, None, None, None, [], "not_offered", [])

    base_limit = min(features.avg_monthly_gmv_3m * Decimal("1.5"), features.annual_gmv_12m * Decimal("0.18"))
    multiplier = {
        "tier_1": Decimal("1.0"),
        "tier_2": Decimal("0.7"),
        "tier_3": Decimal("0.4"),
    }[score_result.risk_tier]
    final_limit = round_to_nearest(base_limit * multiplier, Decimal("50000"))

    if score_result.risk_tier == "tier_1":
        interest_min, interest_max, tenures, status = Decimal("14.0"), Decimal("16.0"), [3, 6, 9], "eligible"
    elif score_result.risk_tier == "tier_2":
        interest_min, interest_max, tenures, status = Decimal("17.0"), Decimal("20.0"), [3, 6, 9], "eligible"
    else:
        interest_min, interest_max, tenures, status = None, None, [3, 6], "manual_review"

    reasons = [
        ReasonData(
            reason_type="offer_adjustment",
            reason_code="credit_limit_generated",
            reason_label="Credit limit generated",
            reason_detail="Working capital limit computed from recent and annual GMV with tier multiplier.",
            metric_name="final_limit",
            metric_value=quantize_2(final_limit),
            benchmark_value=quantize_2(base_limit),
            impact_direction="positive",
        )
    ]
    return CreditOfferResult(
        base_limit=quantize_2(base_limit),
        final_limit=quantize_2(final_limit),
        interest_rate_min=interest_min,
        interest_rate_max=interest_max,
        tenure_options=tenures,
        offer_status=status,
        reasons=reasons,
    )


def build_insurance_offer(
    features: FeatureResult,
    score_result: ScorecardResult,
    decision: str,
    merchant: Merchant,
) -> InsuranceOfferResult:
    if decision == "rejected":
        return InsuranceOfferResult(None, None, None, None, None, "not_offered", [])

    if features.avg_monthly_gmv_3m is None:
        return InsuranceOfferResult(None, None, None, None, None, "not_offered", [])

    coverage_base = min(features.avg_monthly_gmv_3m * Decimal("2"), features.annual_gmv_12m * Decimal("0.25"))
    category_multiplier = {
        "food": Decimal("0.8"),
        "fashion": Decimal("1.0"),
        "electronics": Decimal("1.1"),
        "travel": Decimal("1.2"),
        "health_beauty": Decimal("1.0"),
        "home_lifestyle": Decimal("1.0"),
    }[merchant.category]
    risk_multiplier = {
        "tier_1": Decimal("1.0"),
        "tier_2": Decimal("1.2"),
        "tier_3": Decimal("1.5"),
    }[score_result.risk_tier]
    premium_rate = {
        "tier_1": Decimal("0.008"),
        "tier_2": Decimal("0.012"),
        "tier_3": Decimal("0.018"),
    }[score_result.risk_tier]
    coverage_amount = quantize_2(coverage_base * category_multiplier)
    premium_amount = quantize_2(coverage_amount * premium_rate * risk_multiplier)

    if features.seasonality_pressure_score >= Decimal("1.0"):
        policy_type = "peak_season_revenue_protection"
    elif features.refund_delta_vs_category > Decimal("1.5"):
        policy_type = "order_cancellation_revenue_protection"
    else:
        policy_type = "business_interruption_cover"

    status = "eligible" if score_result.risk_tier in {"tier_1", "tier_2"} and decision == "approved" else "manual_review"
    reasons = [
        ReasonData(
            reason_type="offer_adjustment",
            reason_code="insurance_offer_generated",
            reason_label="Insurance coverage generated",
            reason_detail="Insurance coverage and premium were computed from GMV, category risk, and underwriting tier.",
            metric_name="coverage_amount",
            metric_value=coverage_amount,
            benchmark_value=quantize_2(coverage_base),
            impact_direction="positive",
        )
    ]
    return InsuranceOfferResult(
        coverage_base=quantize_2(coverage_base),
        coverage_amount=coverage_amount,
        premium_rate=premium_rate,
        premium_amount=premium_amount,
        policy_type=policy_type,
        offer_status=status,
        reasons=reasons,
    )
