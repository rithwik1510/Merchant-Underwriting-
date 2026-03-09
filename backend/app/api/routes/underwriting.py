from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import UnderwritingRunListResponse, UnderwritingRunResponse
from app.services.underwriting_service import get_underwriting_run, list_underwriting_runs, run_underwriting_for_merchant


router = APIRouter()


@router.post("/run/{merchant_id}", response_model=UnderwritingRunResponse)
def run_underwriting(merchant_id: str, db: Session = Depends(get_db)) -> UnderwritingRunResponse:
    return run_underwriting_for_merchant(db, merchant_id)


@router.get("/runs", response_model=list[UnderwritingRunListResponse])
def list_runs(db: Session = Depends(get_db)) -> list[UnderwritingRunListResponse]:
    return list_underwriting_runs(db)


@router.get("/runs/{run_id}", response_model=UnderwritingRunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)) -> UnderwritingRunResponse:
    return get_underwriting_run(db, run_id)
