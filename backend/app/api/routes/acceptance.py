from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import OfferAcceptanceRequest, OfferAcceptanceResponse, Phase4ResetResponse
from app.services.acceptance_service import accept_offer, get_offer_acceptance, reset_demo_phase4


router = APIRouter()


@router.post("/offers/{run_id}/accept", response_model=OfferAcceptanceResponse)
def accept_run_offer(run_id: int, request: OfferAcceptanceRequest, db: Session = Depends(get_db)) -> OfferAcceptanceResponse:
    return accept_offer(db, run_id, request)


@router.get("/offers/{run_id}/acceptance", response_model=OfferAcceptanceResponse)
def get_run_acceptance(run_id: int, db: Session = Depends(get_db)) -> OfferAcceptanceResponse:
    return get_offer_acceptance(db, run_id)


@router.post("/offers/{run_id}/reset-demo", response_model=Phase4ResetResponse)
def reset_run_phase4(run_id: int, db: Session = Depends(get_db)) -> Phase4ResetResponse:
    return reset_demo_phase4(db, run_id)
