from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Merchant
from app.schemas import MerchantDetailResponse, MerchantSummaryResponse


router = APIRouter()


@router.get("", response_model=list[MerchantSummaryResponse])
def list_merchants(db: Session = Depends(get_db)) -> list[MerchantSummaryResponse]:
    merchants = db.scalars(select(Merchant).order_by(Merchant.merchant_name)).all()
    return [MerchantSummaryResponse.model_validate(merchant) for merchant in merchants]


@router.get("/{merchant_id}", response_model=MerchantDetailResponse)
def get_merchant(merchant_id: str, db: Session = Depends(get_db)) -> MerchantDetailResponse:
    merchant = db.scalar(select(Merchant).where(Merchant.merchant_id == merchant_id))
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return MerchantDetailResponse.model_validate(merchant)
