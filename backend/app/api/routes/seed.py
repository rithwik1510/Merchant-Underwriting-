from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import SeedInitResponse
from app.services.seed import seed_initial_data


router = APIRouter()


@router.post("/init", response_model=SeedInitResponse)
def initialize_seed_data(db: Session = Depends(get_db)) -> SeedInitResponse:
    return seed_initial_data(db)
