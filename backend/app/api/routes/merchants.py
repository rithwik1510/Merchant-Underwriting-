from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Merchant, UnderwritingRun
from app.schemas import MerchantDetailResponse, MerchantSummaryResponse


router = APIRouter()


@router.get("", response_model=list[MerchantSummaryResponse])
def list_merchants(db: Session = Depends(get_db)) -> list[MerchantSummaryResponse]:
    merchants = db.scalars(select(Merchant).order_by(Merchant.merchant_name)).all()
    runs = db.scalars(
        select(UnderwritingRun)
        .options(selectinload(UnderwritingRun.merchant), selectinload(UnderwritingRun.credit_offer), selectinload(UnderwritingRun.insurance_offer))
        .order_by(UnderwritingRun.created_at.desc(), UnderwritingRun.id.desc())
    ).all()

    latest_by_merchant_id: dict[int, UnderwritingRun] = {}
    for run in runs:
        latest_by_merchant_id.setdefault(run.merchant_id, run)

    response: list[MerchantSummaryResponse] = []
    for merchant in merchants:
        latest_run = latest_by_merchant_id.get(merchant.id)
        response.append(
            MerchantSummaryResponse(
                merchant_id=merchant.merchant_id,
                merchant_name=merchant.merchant_name,
                category=merchant.category,
                seed_intended_outcome=merchant.seed_intended_outcome,
                unique_customer_count=merchant.unique_customer_count,
                customer_return_rate=merchant.customer_return_rate,
                return_and_refund_rate=merchant.return_and_refund_rate,
                registered_whatsapp_number=merchant.registered_whatsapp_number,
                latest_run_id=latest_run.id if latest_run else None,
                latest_decision=latest_run.decision.value if latest_run else None,
                latest_risk_tier=latest_run.risk_tier.value if latest_run else None,
                latest_credit_limit=float(latest_run.credit_offer.final_limit) if latest_run and latest_run.credit_offer.final_limit is not None else None,
                latest_insurance_coverage=float(latest_run.insurance_offer.coverage_amount) if latest_run and latest_run.insurance_offer.coverage_amount is not None else None,
                latest_run_at=latest_run.created_at if latest_run else None,
            )
        )
    return response


@router.get("/{merchant_id}", response_model=MerchantDetailResponse)
def get_merchant(merchant_id: str, db: Session = Depends(get_db)) -> MerchantDetailResponse:
    merchant = db.scalar(select(Merchant).where(Merchant.merchant_id == merchant_id))
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return MerchantDetailResponse.model_validate(merchant)
