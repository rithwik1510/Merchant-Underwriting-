from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    CategoryBenchmark,
    CreditOffer,
    DecisionReason,
    DecisionReasonType,
    FeatureSnapshot,
    InsuranceOffer,
    Merchant,
    OfferStatus,
    PolicyVersion,
    RiskTier,
    UnderwritingDecision,
    UnderwritingRun,
    UnderwritingRunStatus,
)
from app.schemas import (
    CreditOfferResponse,
    DecisionReasonResponse,
    FeatureSnapshotResponse,
    InsuranceOfferResponse,
    MerchantSummaryResponse,
    UnderwritingRunListResponse,
    UnderwritingRunResponse,
)
from app.services.feature_engine import compute_features
from app.services.offer_engine import build_credit_offer, build_insurance_offer
from app.services.policy_engine import evaluate_hard_stops, evaluate_manual_review
from app.services.scorecard_engine import score_merchant
from app.services.underwriting_types import ReasonData, ScorecardResult


def run_underwriting_for_merchant(db: Session, merchant_public_id: str) -> UnderwritingRunResponse:
    merchant = db.scalar(
        select(Merchant)
        .options(selectinload(Merchant.monthly_metrics))
        .where(Merchant.merchant_id == merchant_public_id)
    )
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    benchmark = db.scalar(select(CategoryBenchmark).where(CategoryBenchmark.category == merchant.category))
    policy = db.scalar(select(PolicyVersion).where(PolicyVersion.is_active.is_(True)))
    if not policy:
        raise HTTPException(status_code=500, detail="Active policy not found")

    rules = policy.rules_json
    features = compute_features(merchant, benchmark, rules)
    hard_stops = evaluate_hard_stops(features, merchant, rules)
    manual_review = evaluate_manual_review(features, merchant, rules, benchmark is not None)
    hard_stop_reasons = list(hard_stops.reasons)
    manual_review_reasons = list(manual_review.reasons)
    score_reasons: list[ReasonData] = []
    offer_reasons: list[ReasonData] = []

    if hard_stops.triggered:
        score_result = None
        decision = "rejected"
        risk_tier = "rejected"
        numeric_score = None
    else:
        score_result = score_merchant(features, merchant, benchmark, rules)
        score_reasons = [_component_to_reason(component) for component in score_result.components]
        risk_tier = score_result.risk_tier
        if risk_tier == "tier_1" and (
            features.refund_delta_vs_category > Decimal("0")
            or features.return_rate_delta_vs_category < Decimal("0")
            or features.seasonality_pressure_score > Decimal("0")
        ):
            risk_tier = "tier_2"
            offer_reasons.append(
                ReasonData(
                    reason_type="offer_adjustment",
                    reason_code="tier_capped_to_tier_2",
                    reason_label="Tier capped to Tier 2",
                    reason_detail="Merchant shows some benchmark-relative weakness, so approval is capped below Tier 1.",
                    impact_direction="negative",
                )
            )
        if manual_review.triggered or _has_material_weaknesses(score_result):
            if not manual_review.triggered and _has_material_weaknesses(score_result):
                manual_review_reasons.append(
                    ReasonData(
                        reason_type="manual_review",
                        reason_code="multiple_material_weaknesses",
                        reason_label="Multiple material weaknesses",
                        reason_detail="Two or more important score components underperformed and require manual review.",
                        impact_direction="negative",
                    )
                )
            risk_tier = "tier_3" if risk_tier in {"tier_1", "tier_2"} else risk_tier
        numeric_score = score_result.numeric_score
        if risk_tier == "rejected":
            decision = "rejected"
        elif risk_tier == "tier_3" or manual_review_reasons:
            decision = "manual_review"
        else:
            decision = "approved"

    if score_result is None:
        score_result = ScorecardResult(numeric_score=Decimal("0"), risk_tier="rejected", components=[])

    # Offer pricing must follow the final post-policy risk tier (after capping and review escalation),
    # not the raw scorecard tier from before adjustments.
    score_result_for_offers = ScorecardResult(
        numeric_score=score_result.numeric_score,
        risk_tier=risk_tier,
        components=score_result.components,
    )

    credit_offer_result = build_credit_offer(features, score_result_for_offers, decision)
    insurance_offer_result = build_insurance_offer(features, score_result_for_offers, decision, merchant)

    status = _determine_status(decision)
    run = UnderwritingRun(
        merchant_id=merchant.id,
        policy_version_id=policy.id,
        status=status,
        decision=UnderwritingDecision(decision),
        risk_tier=RiskTier(risk_tier),
        numeric_score=numeric_score,
        usable_history_months=features.usable_history_months,
        hard_stop_triggered=hard_stops.triggered,
        manual_review_triggered=manual_review.triggered or risk_tier == "tier_3",
    )
    db.add(run)
    db.flush()

    db.add(
        FeatureSnapshot(
            underwriting_run_id=run.id,
            avg_monthly_gmv_3m=features.avg_monthly_gmv_3m,
            annual_gmv_12m=features.annual_gmv_12m,
            gmv_growth_3m_pct=features.gmv_growth_3m_pct,
            gmv_growth_12m_pct=features.gmv_growth_12m_pct,
            gmv_volatility_cv=features.gmv_volatility_cv,
            avg_orders_3m=features.avg_orders_3m,
            avg_unique_customers_3m=features.avg_unique_customers_3m,
            customer_efficiency_ratio=features.customer_efficiency_ratio,
            refund_delta_vs_category=features.refund_delta_vs_category,
            return_rate_delta_vs_category=features.return_rate_delta_vs_category,
            aov_position_vs_category_midpoint=features.aov_position_vs_category_midpoint,
            seasonality_pressure_score=features.seasonality_pressure_score,
            recent_gmv_drop_pct=features.recent_gmv_drop_pct,
            merchant_health_score=features.merchant_health_score,
            raw_feature_json=features.raw_feature_json,
        )
    )

    _persist_reasons(db, run.id, hard_stop_reasons)
    _persist_reasons(db, run.id, manual_review_reasons)
    _persist_reasons(db, run.id, score_reasons)
    _persist_reasons(db, run.id, offer_reasons + credit_offer_result.reasons + insurance_offer_result.reasons)

    db.add(
        CreditOffer(
            underwriting_run_id=run.id,
            base_limit=credit_offer_result.base_limit,
            final_limit=credit_offer_result.final_limit,
            interest_rate_min=credit_offer_result.interest_rate_min,
            interest_rate_max=credit_offer_result.interest_rate_max,
            tenure_options_json=credit_offer_result.tenure_options,
            offer_status=OfferStatus(credit_offer_result.offer_status),
        )
    )
    db.add(
        InsuranceOffer(
            underwriting_run_id=run.id,
            coverage_base=insurance_offer_result.coverage_base,
            coverage_amount=insurance_offer_result.coverage_amount,
            premium_rate=insurance_offer_result.premium_rate,
            premium_amount=insurance_offer_result.premium_amount,
            policy_type=insurance_offer_result.policy_type,
            offer_status=OfferStatus(insurance_offer_result.offer_status),
        )
    )
    db.commit()
    return get_underwriting_run(db, run.id)


def list_underwriting_runs(db: Session) -> list[UnderwritingRunListResponse]:
    runs = db.scalars(
        select(UnderwritingRun)
        .options(selectinload(UnderwritingRun.merchant))
        .order_by(UnderwritingRun.created_at.desc())
    ).all()
    return [
        UnderwritingRunListResponse(
            run_id=run.id,
            merchant_id=run.merchant.merchant_id,
            merchant_name=run.merchant.merchant_name,
            status=run.status.value,
            decision=run.decision.value,
            risk_tier=run.risk_tier.value,
            numeric_score=float(run.numeric_score) if run.numeric_score is not None else None,
            created_at=run.created_at,
        )
        for run in runs
    ]


def get_underwriting_run(db: Session, run_id: int) -> UnderwritingRunResponse:
    run = db.scalar(
        select(UnderwritingRun)
        .options(
            selectinload(UnderwritingRun.merchant),
            selectinload(UnderwritingRun.feature_snapshot),
            selectinload(UnderwritingRun.decision_reasons),
            selectinload(UnderwritingRun.credit_offer),
            selectinload(UnderwritingRun.insurance_offer),
            selectinload(UnderwritingRun.policy_version),
        )
        .where(UnderwritingRun.id == run_id)
    )
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")

    grouped = {
        "hard_stop": [],
        "manual_review": [],
        "score_component": [],
        "offer_adjustment": [],
    }
    for reason in run.decision_reasons:
        grouped[reason.reason_type.value].append(
            DecisionReasonResponse(
                reason_code=reason.reason_code,
                reason_label=reason.reason_label,
                reason_detail=reason.reason_detail,
                metric_name=reason.metric_name,
                metric_value=float(reason.metric_value) if reason.metric_value is not None else None,
                benchmark_value=float(reason.benchmark_value) if reason.benchmark_value is not None else None,
                weight=float(reason.weight) if reason.weight is not None else None,
                impact_direction=reason.impact_direction,
            )
        )

    features = run.feature_snapshot
    return UnderwritingRunResponse(
        run_id=run.id,
        merchant=MerchantSummaryResponse.model_validate(run.merchant),
        policy_version=run.policy_version.version_name,
        status=run.status.value,
        decision=run.decision.value,
        risk_tier=run.risk_tier.value,
        numeric_score=float(run.numeric_score) if run.numeric_score is not None else None,
        usable_history_months=run.usable_history_months,
        hard_stop_triggered=run.hard_stop_triggered,
        manual_review_triggered=run.manual_review_triggered,
        features=FeatureSnapshotResponse(
            avg_monthly_gmv_3m=float(features.avg_monthly_gmv_3m) if features.avg_monthly_gmv_3m is not None else None,
            annual_gmv_12m=float(features.annual_gmv_12m),
            gmv_growth_3m_pct=float(features.gmv_growth_3m_pct) if features.gmv_growth_3m_pct is not None else None,
            gmv_growth_12m_pct=float(features.gmv_growth_12m_pct) if features.gmv_growth_12m_pct is not None else None,
            gmv_volatility_cv=float(features.gmv_volatility_cv),
            avg_orders_3m=float(features.avg_orders_3m) if features.avg_orders_3m is not None else None,
            avg_unique_customers_3m=float(features.avg_unique_customers_3m)
            if features.avg_unique_customers_3m is not None
            else None,
            customer_efficiency_ratio=float(features.customer_efficiency_ratio)
            if features.customer_efficiency_ratio is not None
            else None,
            refund_delta_vs_category=float(features.refund_delta_vs_category),
            return_rate_delta_vs_category=float(features.return_rate_delta_vs_category),
            aov_position_vs_category_midpoint=float(features.aov_position_vs_category_midpoint),
            seasonality_pressure_score=float(features.seasonality_pressure_score),
            recent_gmv_drop_pct=float(features.recent_gmv_drop_pct),
            merchant_health_score=float(features.merchant_health_score),
            raw_feature_json=features.raw_feature_json,
        ),
        hard_stop_reasons=grouped["hard_stop"],
        manual_review_reasons=grouped["manual_review"],
        score_reasons=grouped["score_component"],
        offer_adjustments=grouped["offer_adjustment"],
        credit_offer=CreditOfferResponse(
            base_limit=float(run.credit_offer.base_limit) if run.credit_offer.base_limit is not None else None,
            final_limit=float(run.credit_offer.final_limit) if run.credit_offer.final_limit is not None else None,
            interest_rate_min=float(run.credit_offer.interest_rate_min) if run.credit_offer.interest_rate_min is not None else None,
            interest_rate_max=float(run.credit_offer.interest_rate_max) if run.credit_offer.interest_rate_max is not None else None,
            tenure_options=run.credit_offer.tenure_options_json,
            offer_status=run.credit_offer.offer_status.value,
        ),
        insurance_offer=InsuranceOfferResponse(
            coverage_base=float(run.insurance_offer.coverage_base) if run.insurance_offer.coverage_base is not None else None,
            coverage_amount=float(run.insurance_offer.coverage_amount) if run.insurance_offer.coverage_amount is not None else None,
            premium_rate=float(run.insurance_offer.premium_rate) if run.insurance_offer.premium_rate is not None else None,
            premium_amount=float(run.insurance_offer.premium_amount) if run.insurance_offer.premium_amount is not None else None,
            policy_type=run.insurance_offer.policy_type,
            offer_status=run.insurance_offer.offer_status.value,
        ),
        created_at=run.created_at,
    )


def _has_material_weaknesses(score_result) -> bool:
    weak_components = [
        component
        for component in score_result.components
        if component.weight >= Decimal("10") and component.awarded < (component.weight * Decimal("0.55"))
    ]
    return len(weak_components) >= 3


def _determine_status(decision: str) -> UnderwritingRunStatus:
    if decision == "rejected":
        return UnderwritingRunStatus.REJECTED
    if decision == "manual_review":
        return UnderwritingRunStatus.MANUAL_REVIEW
    return UnderwritingRunStatus.COMPLETED


def _persist_reasons(db: Session, run_id: int, reasons: list[ReasonData]) -> None:
    for reason in reasons:
        db.add(
            DecisionReason(
                underwriting_run_id=run_id,
                reason_type=DecisionReasonType(reason.reason_type),
                reason_code=reason.reason_code,
                reason_label=reason.reason_label,
                reason_detail=reason.reason_detail,
                metric_name=reason.metric_name,
                metric_value=reason.metric_value,
                benchmark_value=reason.benchmark_value,
                weight=reason.weight,
                impact_direction=reason.impact_direction,
            )
        )


def _component_to_reason(component) -> ReasonData:
    return ReasonData(
        reason_type="score_component",
        reason_code=component.code,
        reason_label=component.label,
        reason_detail=component.detail,
        metric_name=component.metric_name,
        metric_value=component.metric_value,
        benchmark_value=component.benchmark_value,
        weight=component.weight,
        impact_direction=component.impact_direction,
    )
