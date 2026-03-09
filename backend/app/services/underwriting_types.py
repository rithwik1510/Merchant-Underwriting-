from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReasonData:
    reason_type: str
    reason_code: str
    reason_label: str
    reason_detail: str
    metric_name: str | None = None
    metric_value: Decimal | None = None
    benchmark_value: Decimal | None = None
    weight: Decimal | None = None
    impact_direction: str | None = None


@dataclass(frozen=True)
class FeatureResult:
    usable_history_months: int
    avg_monthly_gmv_3m: Decimal | None
    annual_gmv_12m: Decimal
    gmv_growth_3m_pct: Decimal | None
    gmv_growth_12m_pct: Decimal | None
    gmv_volatility_cv: Decimal
    avg_orders_3m: Decimal | None
    avg_unique_customers_3m: Decimal | None
    customer_efficiency_ratio: Decimal | None
    refund_delta_vs_category: Decimal
    return_rate_delta_vs_category: Decimal
    aov_position_vs_category_midpoint: Decimal
    seasonality_pressure_score: Decimal
    recent_gmv_drop_pct: Decimal
    merchant_health_score: Decimal
    raw_feature_json: dict


@dataclass(frozen=True)
class PolicyCheckResult:
    triggered: bool
    reasons: list[ReasonData]


@dataclass(frozen=True)
class ScoreComponent:
    code: str
    label: str
    awarded: Decimal
    weight: Decimal
    metric_name: str
    metric_value: Decimal | None
    benchmark_value: Decimal | None
    detail: str
    impact_direction: str


@dataclass(frozen=True)
class ScorecardResult:
    numeric_score: Decimal
    risk_tier: str
    components: list[ScoreComponent]


@dataclass(frozen=True)
class CreditOfferResult:
    base_limit: Decimal | None
    final_limit: Decimal | None
    interest_rate_min: Decimal | None
    interest_rate_max: Decimal | None
    tenure_options: list[int]
    offer_status: str
    reasons: list[ReasonData]


@dataclass(frozen=True)
class InsuranceOfferResult:
    coverage_base: Decimal | None
    coverage_amount: Decimal | None
    premium_rate: Decimal | None
    premium_amount: Decimal | None
    policy_type: str | None
    offer_status: str
    reasons: list[ReasonData]
