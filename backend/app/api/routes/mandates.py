from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import MandateSelectBankRequest, MandateSessionResponse, MandateStartRequest, MandateVerifyOtpRequest
from app.services.mandate_service import complete_mandate, get_mandate, select_bank, send_otp, start_mandate, verify_mandate_otp


router = APIRouter()


@router.post("/mandates/{run_id}/start", response_model=MandateSessionResponse)
def start_run_mandate(run_id: int, request: MandateStartRequest, db: Session = Depends(get_db)) -> MandateSessionResponse:
    return start_mandate(db, run_id, request)


@router.post("/mandates/{run_id}/select-bank", response_model=MandateSessionResponse)
def select_run_bank(run_id: int, request: MandateSelectBankRequest, db: Session = Depends(get_db)) -> MandateSessionResponse:
    return select_bank(db, run_id, request)


@router.post("/mandates/{run_id}/send-otp", response_model=MandateSessionResponse)
def send_run_otp(run_id: int, db: Session = Depends(get_db)) -> MandateSessionResponse:
    return send_otp(db, run_id)


@router.post("/mandates/{run_id}/verify-otp", response_model=MandateSessionResponse)
def verify_run_otp(run_id: int, request: MandateVerifyOtpRequest, db: Session = Depends(get_db)) -> MandateSessionResponse:
    return verify_mandate_otp(db, run_id, request)


@router.post("/mandates/{run_id}/complete", response_model=MandateSessionResponse)
def complete_run_mandate(run_id: int, db: Session = Depends(get_db)) -> MandateSessionResponse:
    return complete_mandate(db, run_id)


@router.get("/mandates/{run_id}", response_model=MandateSessionResponse)
def get_run_mandate(run_id: int, db: Session = Depends(get_db)) -> MandateSessionResponse:
    return get_mandate(db, run_id)
