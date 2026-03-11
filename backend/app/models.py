from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from enum import Enum

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum as SqlEnum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    merchant_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    coupon_redemption_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    unique_customer_count: Mapped[int] = mapped_column(nullable=False)
    customer_return_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    avg_order_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    seasonality_index: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    deal_exclusivity_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    return_and_refund_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    registered_whatsapp_number: Mapped[str] = mapped_column(String(30), nullable=False)
    seed_intended_outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    monthly_metrics: Mapped[list["MerchantMonthlyMetric"]] = relationship(
        back_populates="merchant",
        cascade="all, delete-orphan",
        order_by="MerchantMonthlyMetric.metric_month",
    )


class MerchantMonthlyMetric(Base):
    __tablename__ = "merchant_monthly_metrics"
    __table_args__ = (UniqueConstraint("merchant_id", "metric_month", name="uq_merchant_month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    metric_month: Mapped[date] = mapped_column(Date, nullable=False)
    gmv: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    orders_count: Mapped[int] = mapped_column(nullable=False)
    unique_customers: Mapped[int] = mapped_column(nullable=False)
    refund_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    merchant: Mapped["Merchant"] = relationship(back_populates="monthly_metrics")


class CategoryBenchmark(Base):
    __tablename__ = "category_benchmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    avg_refund_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    avg_customer_return_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    avg_order_value_low: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    avg_order_value_high: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    typical_seasonality_low: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    typical_seasonality_high: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    risk_adjustment_factor: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rules_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class UnderwritingRunStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    FAILED = "FAILED"


class UnderwritingDecision(str, Enum):
    APPROVED = "approved"
    MANUAL_REVIEW = "manual_review"
    REJECTED = "rejected"


class RiskTier(str, Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    REJECTED = "rejected"


class DecisionReasonType(str, Enum):
    HARD_STOP = "hard_stop"
    MANUAL_REVIEW = "manual_review"
    SCORE_COMPONENT = "score_component"
    OFFER_ADJUSTMENT = "offer_adjustment"


class OfferStatus(str, Enum):
    ELIGIBLE = "eligible"
    MANUAL_REVIEW = "manual_review"
    NOT_OFFERED = "not_offered"


class LLMGenerationType(str, Enum):
    DECISION_EXPLANATION = "decision_explanation"
    WHATSAPP_MESSAGE = "whatsapp_message"


class LLMGenerationStatus(str, Enum):
    SUCCESS = "success"
    FALLBACK = "fallback"
    FAILED_VALIDATION = "failed_validation"
    FAILED_PROVIDER = "failed_provider"


class AISanityCheckStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    UNAVAILABLE = "unavailable"
    SKIPPED = "skipped"


class WhatsAppMessageType(str, Enum):
    CREDIT_OFFER = "credit_offer"
    INSURANCE_OFFER = "insurance_offer"
    COMBINED_OFFER = "combined_offer"


class WhatsAppDeliveryStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class AcceptedProductType(str, Enum):
    CREDIT = "credit"
    INSURANCE = "insurance"
    COMBINED = "combined"


class AcceptanceVia(str, Enum):
    DASHBOARD = "dashboard"
    WHATSAPP = "whatsapp"
    API = "api"


class MandateStatus(str, Enum):
    INITIATED = "initiated"
    BANK_SELECTED = "bank_selected"
    OTP_SENT = "otp_sent"
    OTP_VERIFIED = "otp_verified"
    UMRN_GENERATED = "umrn_generated"
    COMPLETED = "completed"
    FAILED = "failed"


class UnderwritingRun(Base):
    __tablename__ = "underwriting_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    policy_version_id: Mapped[int] = mapped_column(ForeignKey("policy_versions.id"), nullable=False)
    status: Mapped[UnderwritingRunStatus] = mapped_column(
        SqlEnum(UnderwritingRunStatus, native_enum=False), nullable=False
    )
    decision: Mapped[UnderwritingDecision] = mapped_column(
        SqlEnum(UnderwritingDecision, native_enum=False), nullable=False
    )
    risk_tier: Mapped[RiskTier] = mapped_column(SqlEnum(RiskTier, native_enum=False), nullable=False)
    numeric_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    usable_history_months: Mapped[int] = mapped_column(nullable=False)
    hard_stop_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_review_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    merchant: Mapped[Merchant] = relationship()
    policy_version: Mapped[PolicyVersion] = relationship()
    feature_snapshot: Mapped["FeatureSnapshot"] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    decision_reasons: Mapped[list["DecisionReason"]] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
    )
    credit_offer: Mapped["CreditOffer"] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    insurance_offer: Mapped["InsuranceOffer"] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    llm_generations: Mapped[list["LLMGeneration"]] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        order_by="LLMGeneration.created_at",
    )
    ai_sanity_check: Mapped["AISanityCheck | None"] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    whatsapp_messages: Mapped[list["WhatsAppMessage"]] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        order_by="WhatsAppMessage.created_at",
    )
    offer_acceptance: Mapped["OfferAcceptance | None"] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    mock_nach_mandate: Mapped["MockNachMandate | None"] = relationship(
        back_populates="underwriting_run",
        cascade="all, delete-orphan",
        uselist=False,
    )


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    avg_monthly_gmv_3m: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    annual_gmv_12m: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    gmv_growth_3m_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    gmv_growth_12m_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    gmv_volatility_cv: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    avg_orders_3m: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    avg_unique_customers_3m: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    customer_efficiency_ratio: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    refund_delta_vs_category: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    return_rate_delta_vs_category: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    aov_position_vs_category_midpoint: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    seasonality_pressure_score: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    recent_gmv_drop_pct: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    merchant_health_score: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    raw_feature_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="feature_snapshot")


class DecisionReason(Base):
    __tablename__ = "decision_reasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(ForeignKey("underwriting_runs.id", ondelete="CASCADE"))
    reason_type: Mapped[DecisionReasonType] = mapped_column(
        SqlEnum(DecisionReasonType, native_enum=False), nullable=False
    )
    reason_code: Mapped[str] = mapped_column(String(100), nullable=False)
    reason_label: Mapped[str] = mapped_column(String(150), nullable=False)
    reason_detail: Mapped[str] = mapped_column(String(500), nullable=False)
    metric_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metric_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    benchmark_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    impact_direction: Mapped[str | None] = mapped_column(String(20), nullable=True)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="decision_reasons")


class CreditOffer(Base):
    __tablename__ = "credit_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    base_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    final_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    interest_rate_min: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    interest_rate_max: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    tenure_options_json: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    offer_status: Mapped[OfferStatus] = mapped_column(SqlEnum(OfferStatus, native_enum=False), nullable=False)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="credit_offer")


class InsuranceOffer(Base):
    __tablename__ = "insurance_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    coverage_base: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    coverage_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    premium_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    premium_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    policy_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    offer_status: Mapped[OfferStatus] = mapped_column(SqlEnum(OfferStatus, native_enum=False), nullable=False)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="insurance_offer")


class LLMGeneration(Base):
    __tablename__ = "llm_generations"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    generation_type: Mapped[LLMGenerationType] = mapped_column(
        SqlEnum(LLMGenerationType, native_enum=False), nullable=False
    )
    status: Mapped[LLMGenerationStatus] = mapped_column(
        SqlEnum(LLMGenerationStatus, native_enum=False), nullable=False
    )
    input_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation_errors_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="llm_generations")
    whatsapp_messages: Mapped[list["WhatsAppMessage"]] = relationship(back_populates="llm_generation")


class AISanityCheck(Base):
    __tablename__ = "ai_sanity_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[AISanityCheckStatus] = mapped_column(
        SqlEnum(AISanityCheckStatus, native_enum=False), nullable=False
    )
    issue_codes_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    notes_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    suggested_explanation_focus_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    suggested_message_focus_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    input_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation_errors_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="ai_sanity_check")


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), nullable=False
    )
    llm_generation_id: Mapped[int | None] = mapped_column(ForeignKey("llm_generations.id"), nullable=True)
    recipient_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    message_type: Mapped[WhatsAppMessageType] = mapped_column(
        SqlEnum(WhatsAppMessageType, native_enum=False), nullable=False
    )
    content_text: Mapped[str] = mapped_column(String(2000), nullable=False)
    twilio_message_sid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    delivery_status: Mapped[WhatsAppDeliveryStatus] = mapped_column(
        SqlEnum(WhatsAppDeliveryStatus, native_enum=False), nullable=False
    )
    provider_response_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="whatsapp_messages")
    llm_generation: Mapped[LLMGeneration | None] = relationship(back_populates="whatsapp_messages")


class OfferAcceptance(Base):
    __tablename__ = "offer_acceptances"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    accepted_product_type: Mapped[AcceptedProductType] = mapped_column(
        SqlEnum(AcceptedProductType, native_enum=False), nullable=False
    )
    accepted_by_name: Mapped[str] = mapped_column(String(120), nullable=False)
    accepted_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    accepted_via: Mapped[AcceptanceVia] = mapped_column(
        SqlEnum(AcceptanceVia, native_enum=False), nullable=False
    )
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    acceptance_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="offer_acceptance")
    mock_nach_mandate: Mapped["MockNachMandate | None"] = relationship(
        back_populates="offer_acceptance",
        uselist=False,
    )


class MockNachMandate(Base):
    __tablename__ = "mock_nach_mandates"

    id: Mapped[int] = mapped_column(primary_key=True)
    underwriting_run_id: Mapped[int] = mapped_column(
        ForeignKey("underwriting_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    offer_acceptance_id: Mapped[int] = mapped_column(
        ForeignKey("offer_acceptances.id", ondelete="CASCADE"), nullable=False
    )
    mandate_status: Mapped[MandateStatus] = mapped_column(
        SqlEnum(MandateStatus, native_enum=False), nullable=False
    )
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_holder_name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_number_masked: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ifsc_masked: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mobile_number: Mapped[str] = mapped_column(String(30), nullable=False)
    otp_code_hash: Mapped[str | None] = mapped_column(String(200), nullable=True)
    otp_last_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    otp_attempt_count: Mapped[int] = mapped_column(default=0, nullable=False)
    umrn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mandate_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    underwriting_run: Mapped[UnderwritingRun] = relationship(back_populates="mock_nach_mandate")
    offer_acceptance: Mapped[OfferAcceptance] = relationship(back_populates="mock_nach_mandate")
