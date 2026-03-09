from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import PolicyVersion
from app.schemas import PolicyVersionResponse


router = APIRouter()


@router.get("/active", response_model=PolicyVersionResponse)
def get_active_policy(db: Session = Depends(get_db)) -> PolicyVersionResponse:
    policy = db.scalar(select(PolicyVersion).where(PolicyVersion.is_active.is_(True)))
    if not policy:
        raise HTTPException(status_code=404, detail="Active policy not found")
    return PolicyVersionResponse.model_validate(policy)
