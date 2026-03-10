from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import AcceptanceVia, AcceptedProductType, OfferAcceptance, UnderwritingRun
from app.schemas import OfferAcceptanceRequest, OfferAcceptanceResponse, Phase4ResetResponse


def accept_offer(db: Session, run_id: int, payload: OfferAcceptanceRequest) -> OfferAcceptanceResponse:
    run = db.scalar(
        select(UnderwritingRun)
        .options(selectinload(UnderwritingRun.credit_offer), selectinload(UnderwritingRun.insurance_offer), selectinload(UnderwritingRun.offer_acceptance))
        .where(UnderwritingRun.id == run_id)
    )
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")
    if run.decision.value == "rejected":
        raise HTTPException(status_code=400, detail="Rejected runs cannot be accepted")

    accepted_product_type = AcceptedProductType(payload.accepted_product_type)
    _validate_product_acceptance(run, accepted_product_type)

    if run.offer_acceptance:
        return _map_acceptance(run.offer_acceptance)

    acceptance = OfferAcceptance(
        underwriting_run_id=run.id,
        accepted_product_type=accepted_product_type,
        accepted_by_name=payload.accepted_by_name,
        accepted_phone=payload.accepted_phone,
        accepted_via=AcceptanceVia(payload.accepted_via),
        acceptance_notes=payload.acceptance_notes,
    )
    db.add(acceptance)
    db.commit()
    db.refresh(acceptance)
    return _map_acceptance(acceptance)


def get_offer_acceptance(db: Session, run_id: int) -> OfferAcceptanceResponse:
    acceptance = db.scalar(select(OfferAcceptance).where(OfferAcceptance.underwriting_run_id == run_id))
    if not acceptance:
        raise HTTPException(status_code=404, detail="Offer acceptance not found")
    return _map_acceptance(acceptance)


def reset_demo_phase4(db: Session, run_id: int) -> Phase4ResetResponse:
    run = db.scalar(
        select(UnderwritingRun)
        .options(selectinload(UnderwritingRun.offer_acceptance), selectinload(UnderwritingRun.mock_nach_mandate))
        .where(UnderwritingRun.id == run_id)
    )
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")

    if run.mock_nach_mandate is not None:
        db.delete(run.mock_nach_mandate)
    if run.offer_acceptance is not None:
        db.delete(run.offer_acceptance)

    db.commit()
    return Phase4ResetResponse(run_id=run_id, reset=True)


def _validate_product_acceptance(run: UnderwritingRun, accepted_product_type: AcceptedProductType) -> None:
    credit_allowed = run.credit_offer.offer_status.value in {"eligible", "manual_review"}
    insurance_allowed = run.insurance_offer.offer_status.value in {"eligible", "manual_review"}
    if accepted_product_type == AcceptedProductType.CREDIT and not credit_allowed:
        raise HTTPException(status_code=400, detail="Credit offer is not available for acceptance")
    if accepted_product_type == AcceptedProductType.INSURANCE and not insurance_allowed:
        raise HTTPException(status_code=400, detail="Insurance offer is not available for acceptance")
    if accepted_product_type == AcceptedProductType.COMBINED and not (credit_allowed and insurance_allowed):
        raise HTTPException(status_code=400, detail="Combined acceptance requires both offers to be available")


def _map_acceptance(acceptance: OfferAcceptance) -> OfferAcceptanceResponse:
    return OfferAcceptanceResponse(
        id=acceptance.id,
        run_id=acceptance.underwriting_run_id,
        accepted_product_type=acceptance.accepted_product_type.value,
        accepted_by_name=acceptance.accepted_by_name,
        accepted_phone=acceptance.accepted_phone,
        accepted_via=acceptance.accepted_via.value,
        accepted_at=acceptance.accepted_at,
        acceptance_notes=acceptance.acceptance_notes,
        mandate_can_start=True,
    )
