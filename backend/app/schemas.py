from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class MerchantMonthlyMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_month: date
    gmv: Decimal
    orders_count: int
    unique_customers: int
    refund_rate: Decimal


class MerchantSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: str
    merchant_name: str
    category: str
    seed_intended_outcome: str
    unique_customer_count: int
    customer_return_rate: Decimal
    return_and_refund_rate: Decimal
    registered_whatsapp_number: str
    latest_run_id: int | None = None
    latest_decision: str | None = None
    latest_risk_tier: str | None = None
    latest_credit_limit: float | None = None
    latest_insurance_coverage: float | None = None
    latest_run_at: datetime | None = None


class MerchantDetailResponse(MerchantSummaryResponse):
    coupon_redemption_rate: Decimal
    avg_order_value: Decimal
    seasonality_index: Decimal
    deal_exclusivity_rate: Decimal
    created_at: datetime
    updated_at: datetime
    monthly_metrics: list[MerchantMonthlyMetricResponse]


class CategoryBenchmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    avg_refund_rate: Decimal
    avg_customer_return_rate: Decimal
    avg_order_value_low: Decimal
    avg_order_value_high: Decimal
    typical_seasonality_low: Decimal
    typical_seasonality_high: Decimal
    risk_adjustment_factor: Decimal


class PolicyVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_name: str
    is_active: bool
    rules_json: dict[str, Any]
    created_at: datetime


class SeedInitResponse(BaseModel):
    merchants_created: int
    benchmarks_created: int
    monthly_metrics_created: int
    policy_created: bool


class DecisionReasonResponse(BaseModel):
    reason_code: str
    reason_label: str
    reason_detail: str
    metric_name: str | None
    metric_value: float | None
    benchmark_value: float | None
    weight: float | None
    impact_direction: str | None


class FeatureSnapshotResponse(BaseModel):
    avg_monthly_gmv_3m: float | None
    annual_gmv_12m: float
    gmv_growth_3m_pct: float | None
    gmv_growth_12m_pct: float | None
    gmv_volatility_cv: float
    avg_orders_3m: float | None
    avg_unique_customers_3m: float | None
    customer_efficiency_ratio: float | None
    refund_delta_vs_category: float
    return_rate_delta_vs_category: float
    aov_position_vs_category_midpoint: float
    seasonality_pressure_score: float
    recent_gmv_drop_pct: float
    merchant_health_score: float
    raw_feature_json: dict[str, Any]


class CreditOfferResponse(BaseModel):
    base_limit: float | None
    final_limit: float | None
    interest_rate_min: float | None
    interest_rate_max: float | None
    tenure_options: list[int]
    offer_status: str


class InsuranceOfferResponse(BaseModel):
    coverage_base: float | None
    coverage_amount: float | None
    premium_rate: float | None
    premium_amount: float | None
    policy_type: str | None
    offer_status: str


class UnderwritingRunListResponse(BaseModel):
    run_id: int
    merchant_id: str
    merchant_name: str
    status: str
    decision: str
    risk_tier: str
    numeric_score: float | None
    created_at: datetime


class UnderwritingRunResponse(BaseModel):
    run_id: int
    merchant: MerchantSummaryResponse
    policy_version: str
    status: str
    decision: str
    risk_tier: str
    numeric_score: float | None
    usable_history_months: int
    hard_stop_triggered: bool
    manual_review_triggered: bool
    features: FeatureSnapshotResponse
    hard_stop_reasons: list[DecisionReasonResponse]
    manual_review_reasons: list[DecisionReasonResponse]
    score_reasons: list[DecisionReasonResponse]
    offer_adjustments: list[DecisionReasonResponse]
    credit_offer: CreditOfferResponse
    insurance_offer: InsuranceOfferResponse
    created_at: datetime


class ExplanationContentResponse(BaseModel):
    generation_id: int
    provider_name: str
    model_name: str
    generation_type: str
    status: str
    output_payload_json: dict[str, Any]
    validation_errors_json: list[str] | None
    created_at: datetime


class LLMProbeRequest(BaseModel):
    provider: str
    api_key_override: str | None = None
    model_override: str | None = None


class LLMProbeResponse(BaseModel):
    provider: str
    model: str
    ok: bool
    status: str
    latency_ms: int | None = None
    used_override_key: bool = False
    error_detail: str | None = None


class LLMSettingsResponse(BaseModel):
    provider: str
    lmstudio_base_url: str
    lmstudio_model: str
    claude_model: str
    claude_base_url: str
    claude_api_key_configured: bool
    claude_api_key_masked: str | None = None


class LLMSettingsUpdateRequest(BaseModel):
    provider: str
    lmstudio_base_url: str | None = None
    lmstudio_model: str | None = None
    claude_model: str | None = None
    claude_base_url: str | None = None
    claude_api_key: str | None = None


class WhatsAppDraftRequest(BaseModel):
    message_type: str = "combined_offer"


class WhatsAppSendRequest(BaseModel):
    recipient_phone: str | None = None
    message_type: str = "combined_offer"


class WhatsAppMessageResponse(BaseModel):
    id: int
    llm_generation_id: int | None
    recipient_phone: str
    message_type: str
    content_text: str
    twilio_message_sid: str | None
    delivery_status: str
    provider_response_json: dict[str, Any] | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class CommunicationsResponse(BaseModel):
    latest_explanation: ExplanationContentResponse | None
    latest_whatsapp_draft: ExplanationContentResponse | None
    whatsapp_messages: list[WhatsAppMessageResponse]


class OfferAcceptanceRequest(BaseModel):
    accepted_product_type: str
    accepted_by_name: str
    accepted_phone: str
    accepted_via: str
    acceptance_notes: str | None = None


class OfferAcceptanceResponse(BaseModel):
    id: int
    run_id: int
    accepted_product_type: str
    accepted_by_name: str
    accepted_phone: str
    accepted_via: str
    accepted_at: datetime
    acceptance_notes: str | None
    mandate_can_start: bool


class Phase4ResetResponse(BaseModel):
    run_id: int
    reset: bool


class MandateStartRequest(BaseModel):
    account_holder_name: str
    mobile_number: str


class MandateSelectBankRequest(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: str


class MandateVerifyOtpRequest(BaseModel):
    otp: str


class MandateSessionResponse(BaseModel):
    id: int
    run_id: int
    acceptance_id: int
    accepted_product_type: str
    mandate_status: str
    account_holder_name: str
    bank_name: str | None
    account_number_masked: str | None
    ifsc_masked: str | None
    mobile_number_masked: str
    otp_attempt_count: int
    remaining_attempts: int
    umrn: str | None
    mandate_reference: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    demo_otp: str | None = None
