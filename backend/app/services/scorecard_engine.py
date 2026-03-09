from __future__ import annotations

from decimal import Decimal

from app.models import CategoryBenchmark, Merchant
from app.services.underwriting_math import clamp_decimal, quantize_2, safe_div
from app.services.underwriting_types import FeatureResult, ScoreComponent, ScorecardResult


def score_merchant(
    features: FeatureResult,
    merchant: Merchant,
    benchmark: CategoryBenchmark | None,
    policy_rules: dict,
) -> ScorecardResult:
    weights = {key: Decimal(str(value)) for key, value in policy_rules["score_weights"].items()}
    components = [
        _gmv_growth_component(features, weights["gmv_growth"]),
        _refund_component(features, weights["refund_behavior"]),
        _return_rate_component(features, weights["customer_return_rate"]),
        _customer_scale_component(features, merchant, weights["customer_scale_growth"]),
        _aov_stability_component(features, merchant, benchmark, weights["aov_stability"]),
        _seasonality_component(features, merchant, benchmark, weights["seasonality_pressure"]),
        _coupon_component(merchant, weights["coupon_redemption_quality"]),
        _exclusivity_component(merchant, weights["deal_exclusivity_quality"]),
    ]

    total_score = quantize_2(sum(component.awarded for component in components))
    boundaries = policy_rules["tier_boundaries"]
    if total_score >= Decimal(str(boundaries["tier_1_min"])):
        risk_tier = "tier_1"
    elif total_score >= Decimal(str(boundaries["tier_2_min"])):
        risk_tier = "tier_2"
    elif total_score >= Decimal(str(boundaries["tier_3_min"])):
        risk_tier = "tier_3"
    else:
        risk_tier = "rejected"

    return ScorecardResult(numeric_score=total_score, risk_tier=risk_tier, components=components)


def _gmv_growth_component(features: FeatureResult, weight: Decimal) -> ScoreComponent:
    growth_12 = features.gmv_growth_12m_pct or Decimal("0")
    growth_3 = features.gmv_growth_3m_pct or Decimal("0")
    normalized = clamp_decimal((growth_12 + Decimal("10")) / Decimal("50"), Decimal("0"), Decimal("1"))
    if growth_3 < 0:
        normalized *= Decimal("0.7")
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="gmv_growth",
        label="GMV growth and trend quality",
        awarded=awarded,
        weight=weight,
        metric_name="gmv_growth_12m_pct",
        metric_value=growth_12,
        benchmark_value=Decimal("0"),
        detail="Scores long-term GMV growth and penalizes weak recent momentum.",
        impact_direction="positive" if awarded >= (weight / 2) else "negative",
    )


def _refund_component(features: FeatureResult, weight: Decimal) -> ScoreComponent:
    delta = features.refund_delta_vs_category
    normalized = clamp_decimal(Decimal("1") - safe_div(max(delta, Decimal("0")), Decimal("8")), Decimal("0"), Decimal("1"))
    if delta < 0:
        normalized = clamp_decimal(normalized + Decimal("0.1"), Decimal("0"), Decimal("1"))
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="refund_behavior",
        label="Refund behavior",
        awarded=awarded,
        weight=weight,
        metric_name="refund_delta_vs_category",
        metric_value=delta,
        benchmark_value=Decimal("0"),
        detail="Compares merchant refund rate against category benchmark.",
        impact_direction="positive" if delta <= 0 else "negative",
    )


def _return_rate_component(features: FeatureResult, weight: Decimal) -> ScoreComponent:
    delta = features.return_rate_delta_vs_category
    normalized = clamp_decimal((delta + Decimal("20")) / Decimal("40"), Decimal("0"), Decimal("1"))
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="customer_return_rate",
        label="Customer return rate strength",
        awarded=awarded,
        weight=weight,
        metric_name="return_rate_delta_vs_category",
        metric_value=delta,
        benchmark_value=Decimal("0"),
        detail="Rewards repeat-customer performance relative to the category.",
        impact_direction="positive" if delta >= 0 else "negative",
    )


def _customer_scale_component(features: FeatureResult, merchant: Merchant, weight: Decimal) -> ScoreComponent:
    base = clamp_decimal(Decimal(merchant.unique_customer_count) / Decimal("20000"), Decimal("0"), Decimal("1"))
    trend = clamp_decimal((features.gmv_growth_3m_pct or Decimal("0") + Decimal("15")) / Decimal("30"), Decimal("0"), Decimal("1"))
    normalized = (base * Decimal("0.6")) + (trend * Decimal("0.4"))
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="customer_scale_growth",
        label="Customer scale and growth",
        awarded=awarded,
        weight=weight,
        metric_name="unique_customer_count",
        metric_value=Decimal(merchant.unique_customer_count),
        benchmark_value=Decimal("20000"),
        detail="Uses merchant customer base size with recent growth trend as support.",
        impact_direction="positive" if awarded >= (weight / 2) else "negative",
    )


def _aov_stability_component(
    features: FeatureResult,
    merchant: Merchant,
    benchmark: CategoryBenchmark | None,
    weight: Decimal,
) -> ScoreComponent:
    if benchmark:
        band_half = (Decimal(benchmark.avg_order_value_high) - Decimal(benchmark.avg_order_value_low)) / Decimal("2")
        fit = Decimal("1") - safe_div(abs(features.aov_position_vs_category_midpoint), max(band_half, Decimal("1")))
        fit = clamp_decimal(fit, Decimal("0"), Decimal("1"))
    else:
        fit = Decimal("0.5")
    volatility_penalty = clamp_decimal(Decimal("1") - Decimal(features.gmv_volatility_cv), Decimal("0"), Decimal("1"))
    normalized = (fit * Decimal("0.7")) + (volatility_penalty * Decimal("0.3"))
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="aov_stability",
        label="AOV stability",
        awarded=awarded,
        weight=weight,
        metric_name="avg_order_value",
        metric_value=Decimal(merchant.avg_order_value),
        benchmark_value=Decimal("0"),
        detail="Rewards fit within category price band and penalizes instability.",
        impact_direction="positive" if awarded >= (weight / 2) else "negative",
    )


def _seasonality_component(
    features: FeatureResult,
    merchant: Merchant,
    benchmark: CategoryBenchmark | None,
    weight: Decimal,
) -> ScoreComponent:
    normalized = Decimal("1") - Decimal(features.seasonality_pressure_score)
    if benchmark and Decimal(merchant.seasonality_index) > Decimal(benchmark.typical_seasonality_high):
        normalized *= Decimal("0.7")
    awarded = quantize_2(weight * clamp_decimal(normalized, Decimal("0"), Decimal("1")))
    return ScoreComponent(
        code="seasonality_pressure",
        label="Seasonality pressure",
        awarded=awarded,
        weight=weight,
        metric_name="seasonality_index",
        metric_value=Decimal(merchant.seasonality_index),
        benchmark_value=Decimal(benchmark.typical_seasonality_high) if benchmark else None,
        detail="Penalizes merchants with seasonality above category comfort band.",
        impact_direction="positive" if awarded >= (weight / 2) else "negative",
    )


def _coupon_component(merchant: Merchant, weight: Decimal) -> ScoreComponent:
    rate = Decimal(merchant.coupon_redemption_rate)
    if rate < Decimal("20"):
        normalized = Decimal("0.45")
    elif rate <= Decimal("45"):
        normalized = Decimal("1.0")
    elif rate <= Decimal("55"):
        normalized = Decimal("0.75")
    else:
        normalized = Decimal("0.55")
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="coupon_redemption_quality",
        label="Coupon redemption quality",
        awarded=awarded,
        weight=weight,
        metric_name="coupon_redemption_rate",
        metric_value=rate,
        benchmark_value=None,
        detail="Rewards healthy deal adoption but penalizes excessive promotion dependence.",
        impact_direction="positive" if awarded >= (weight / 2) else "negative",
    )


def _exclusivity_component(merchant: Merchant, weight: Decimal) -> ScoreComponent:
    rate = Decimal(merchant.deal_exclusivity_rate)
    normalized = clamp_decimal(rate / Decimal("50"), Decimal("0"), Decimal("1"))
    awarded = quantize_2(weight * normalized)
    return ScoreComponent(
        code="deal_exclusivity_quality",
        label="Deal exclusivity quality",
        awarded=awarded,
        weight=weight,
        metric_name="deal_exclusivity_rate",
        metric_value=rate,
        benchmark_value=Decimal("50"),
        detail="Provides a small bonus for merchants with stronger exclusivity behavior.",
        impact_direction="positive" if awarded >= (weight / 2) else "negative",
    )
