from __future__ import annotations

from decimal import Decimal

from app.models import Merchant
from app.services.underwriting_types import FeatureResult, PolicyCheckResult, ReasonData


def evaluate_hard_stops(features: FeatureResult, merchant: Merchant, policy_rules: dict) -> PolicyCheckResult:
    thresholds = policy_rules["hard_stop_thresholds"]
    reasons: list[ReasonData] = []

    if features.usable_history_months < thresholds["min_usable_history_months"]:
        reasons.append(
            ReasonData(
                reason_type="hard_stop",
                reason_code="insufficient_history",
                reason_label="Insufficient history",
                reason_detail=f"Merchant has {features.usable_history_months} usable months, below the required {thresholds['min_usable_history_months']}.",
                metric_name="usable_history_months",
                metric_value=Decimal(features.usable_history_months),
                benchmark_value=Decimal(thresholds["min_usable_history_months"]),
                impact_direction="negative",
            )
        )

    if features.avg_monthly_gmv_3m is None or features.avg_monthly_gmv_3m < Decimal(str(thresholds["min_avg_monthly_gmv_3m"])):
        reasons.append(
            ReasonData(
                reason_type="hard_stop",
                reason_code="low_recent_gmv",
                reason_label="Recent GMV below minimum",
                reason_detail="Average monthly GMV over the last 3 months is below policy minimum.",
                metric_name="avg_monthly_gmv_3m",
                metric_value=features.avg_monthly_gmv_3m,
                benchmark_value=Decimal(str(thresholds["min_avg_monthly_gmv_3m"])),
                impact_direction="negative",
            )
        )

    if Decimal(merchant.return_and_refund_rate) > Decimal(str(thresholds["max_refund_rate"])):
        reasons.append(
            ReasonData(
                reason_type="hard_stop",
                reason_code="refund_rate_too_high",
                reason_label="Refund rate too high",
                reason_detail="Merchant refund rate exceeds the maximum hard-stop threshold.",
                metric_name="return_and_refund_rate",
                metric_value=Decimal(merchant.return_and_refund_rate),
                benchmark_value=Decimal(str(thresholds["max_refund_rate"])),
                impact_direction="negative",
            )
        )

    if Decimal(merchant.customer_return_rate) < Decimal(str(thresholds["min_customer_return_rate"])):
        reasons.append(
            ReasonData(
                reason_type="hard_stop",
                reason_code="return_rate_too_low",
                reason_label="Customer return rate too low",
                reason_detail="Merchant repeat customer performance is below the minimum policy threshold.",
                metric_name="customer_return_rate",
                metric_value=Decimal(merchant.customer_return_rate),
                benchmark_value=Decimal(str(thresholds["min_customer_return_rate"])),
                impact_direction="negative",
            )
        )

    return PolicyCheckResult(triggered=bool(reasons), reasons=reasons)


def evaluate_manual_review(
    features: FeatureResult,
    merchant: Merchant,
    policy_rules: dict,
    benchmark_present: bool,
) -> PolicyCheckResult:
    thresholds = policy_rules["manual_review_thresholds"]
    reasons: list[ReasonData] = []

    if Decimal(features.gmv_volatility_cv) > Decimal(str(thresholds["max_gmv_volatility_cv"])):
        reasons.append(
            ReasonData(
                reason_type="manual_review",
                reason_code="high_gmv_volatility",
                reason_label="High GMV volatility",
                reason_detail="Merchant GMV volatility is above the manual-review threshold.",
                metric_name="gmv_volatility_cv",
                metric_value=Decimal(features.gmv_volatility_cv),
                benchmark_value=Decimal(str(thresholds["max_gmv_volatility_cv"])),
                impact_direction="negative",
            )
        )

    if Decimal(merchant.seasonality_index) > Decimal(str(thresholds["max_seasonality_index"])):
        reasons.append(
            ReasonData(
                reason_type="manual_review",
                reason_code="high_seasonality",
                reason_label="High seasonality pressure",
                reason_detail="Merchant seasonality is above the automatic approval threshold.",
                metric_name="seasonality_index",
                metric_value=Decimal(merchant.seasonality_index),
                benchmark_value=Decimal(str(thresholds["max_seasonality_index"])),
                impact_direction="negative",
            )
        )

    if Decimal(features.recent_gmv_drop_pct) > Decimal(str(thresholds["max_recent_gmv_drop_pct"])):
        reasons.append(
            ReasonData(
                reason_type="manual_review",
                reason_code="recent_gmv_drop",
                reason_label="Recent GMV drop detected",
                reason_detail="Recent 3-month GMV dropped beyond the review threshold.",
                metric_name="recent_gmv_drop_pct",
                metric_value=Decimal(features.recent_gmv_drop_pct),
                benchmark_value=Decimal(str(thresholds["max_recent_gmv_drop_pct"])),
                impact_direction="negative",
            )
        )

    if not benchmark_present:
        reasons.append(
            ReasonData(
                reason_type="manual_review",
                reason_code="missing_benchmark",
                reason_label="Missing category benchmark",
                reason_detail="Benchmark data is unavailable for the merchant category.",
                metric_name="benchmark_present",
                metric_value=Decimal("0"),
                benchmark_value=Decimal("1"),
                impact_direction="negative",
            )
        )

    return PolicyCheckResult(triggered=bool(reasons), reasons=reasons)
