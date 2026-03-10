from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import MockNachMandate, MandateStatus, OfferAcceptance, UnderwritingRun
from app.schemas import MandateSelectBankRequest, MandateSessionResponse, MandateStartRequest, MandateVerifyOtpRequest
from app.services.mandate_utils import (
    generate_demo_otp,
    generate_mandate_reference,
    generate_umrn,
    hash_otp,
    mask_account_number,
    mask_ifsc,
    mask_mobile,
    verify_otp,
)


def start_mandate(db: Session, run_id: int, payload: MandateStartRequest) -> MandateSessionResponse:
    run, acceptance, mandate = _load_phase4_context(db, run_id)
    if not acceptance:
        raise HTTPException(status_code=400, detail="Offer must be accepted before mandate can start")
    if mandate:
        return _map_mandate(mandate)

    mandate = MockNachMandate(
        underwriting_run_id=run.id,
        offer_acceptance_id=acceptance.id,
        mandate_status=MandateStatus.INITIATED,
        account_holder_name=payload.account_holder_name,
        mobile_number=payload.mobile_number,
    )
    db.add(mandate)
    db.commit()
    db.refresh(mandate)
    return _map_mandate(mandate)


def select_bank(db: Session, run_id: int, payload: MandateSelectBankRequest) -> MandateSessionResponse:
    _, _, mandate = _require_mandate_context(db, run_id)
    if mandate.mandate_status != MandateStatus.INITIATED:
        raise HTTPException(status_code=400, detail="Bank can only be selected after mandate initiation")
    mandate.bank_name = payload.bank_name
    mandate.account_number_masked = mask_account_number(payload.account_number)
    mandate.ifsc_masked = mask_ifsc(payload.ifsc_code)
    mandate.mandate_status = MandateStatus.BANK_SELECTED
    db.commit()
    db.refresh(mandate)
    return _map_mandate(mandate)


def send_otp(db: Session, run_id: int) -> MandateSessionResponse:
    _, _, mandate = _require_mandate_context(db, run_id)
    if mandate.mandate_status != MandateStatus.BANK_SELECTED:
        raise HTTPException(status_code=400, detail="OTP can only be sent after bank selection")
    otp = generate_demo_otp()
    mandate.otp_code_hash = hash_otp(otp)
    mandate.otp_last_sent_at = datetime.now(timezone.utc)
    mandate.otp_attempt_count = 0
    mandate.mandate_status = MandateStatus.OTP_SENT
    db.commit()
    db.refresh(mandate)
    return _map_mandate(mandate, demo_otp=otp if get_settings().app_env != "production" else None)


def verify_mandate_otp(db: Session, run_id: int, payload: MandateVerifyOtpRequest) -> MandateSessionResponse:
    _, _, mandate = _require_mandate_context(db, run_id)
    if mandate.mandate_status != MandateStatus.OTP_SENT:
        raise HTTPException(status_code=400, detail="OTP can only be verified after it has been sent")
    if verify_otp(payload.otp, mandate.otp_code_hash):
        mandate.mandate_status = MandateStatus.OTP_VERIFIED
        db.commit()
        db.refresh(mandate)
        return _map_mandate(mandate)

    mandate.otp_attempt_count += 1
    if mandate.otp_attempt_count >= 3:
        mandate.mandate_status = MandateStatus.FAILED
        mandate.failure_reason = "Maximum OTP attempts exceeded"
    db.commit()
    db.refresh(mandate)
    return _map_mandate(mandate)


def complete_mandate(db: Session, run_id: int) -> MandateSessionResponse:
    _, acceptance, mandate = _require_mandate_context(db, run_id)
    if mandate.mandate_status != MandateStatus.OTP_VERIFIED:
        raise HTTPException(status_code=400, detail="Mandate can only be completed after OTP verification")
    if not mandate.umrn:
        mandate.umrn = generate_umrn(run_id)
        mandate.mandate_reference = generate_mandate_reference(run_id, acceptance.id)
        mandate.mandate_status = MandateStatus.UMRN_GENERATED
    mandate.mandate_status = MandateStatus.COMPLETED
    mandate.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mandate)
    return _map_mandate(mandate)


def get_mandate(db: Session, run_id: int) -> MandateSessionResponse:
    _, _, mandate = _require_mandate_context(db, run_id)
    return _map_mandate(mandate)


def _load_phase4_context(db: Session, run_id: int) -> tuple[UnderwritingRun | None, OfferAcceptance | None, MockNachMandate | None]:
    run = db.scalar(
        select(UnderwritingRun)
        .options(selectinload(UnderwritingRun.offer_acceptance), selectinload(UnderwritingRun.mock_nach_mandate))
        .where(UnderwritingRun.id == run_id)
    )
    if not run:
        return None, None, None
    return run, run.offer_acceptance, run.mock_nach_mandate


def _require_mandate_context(db: Session, run_id: int) -> tuple[UnderwritingRun, OfferAcceptance, MockNachMandate]:
    run, acceptance, mandate = _load_phase4_context(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")
    if not acceptance:
        raise HTTPException(status_code=404, detail="Offer acceptance not found")
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")
    return run, acceptance, mandate


def _map_mandate(mandate: MockNachMandate, demo_otp: str | None = None) -> MandateSessionResponse:
    return MandateSessionResponse(
        id=mandate.id,
        run_id=mandate.underwriting_run_id,
        acceptance_id=mandate.offer_acceptance_id,
        accepted_product_type=mandate.offer_acceptance.accepted_product_type.value,
        mandate_status=mandate.mandate_status.value,
        account_holder_name=mandate.account_holder_name,
        bank_name=mandate.bank_name,
        account_number_masked=mandate.account_number_masked,
        ifsc_masked=mandate.ifsc_masked,
        mobile_number_masked=mask_mobile(mandate.mobile_number),
        otp_attempt_count=mandate.otp_attempt_count,
        remaining_attempts=max(0, 3 - mandate.otp_attempt_count),
        umrn=mandate.umrn,
        mandate_reference=mandate.mandate_reference,
        failure_reason=mandate.failure_reason,
        created_at=mandate.created_at,
        updated_at=mandate.updated_at,
        completed_at=mandate.completed_at,
        demo_otp=demo_otp,
    )
