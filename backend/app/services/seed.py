from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CategoryBenchmark, Merchant, MerchantMonthlyMetric, PolicyVersion
from app.schemas import SeedInitResponse
from app.seed_data import ACTIVE_POLICY, BENCHMARKS, MERCHANTS


def seed_initial_data(db: Session) -> SeedInitResponse:
    benchmarks_created = _seed_benchmarks(db)
    merchants_created, monthly_metrics_created = _seed_merchants(db)
    policy_created = _seed_policy(db)
    db.commit()
    return SeedInitResponse(
        merchants_created=merchants_created,
        benchmarks_created=benchmarks_created,
        monthly_metrics_created=monthly_metrics_created,
        policy_created=policy_created,
    )


def _seed_benchmarks(db: Session) -> int:
    created = 0
    for benchmark_data in BENCHMARKS:
        existing = db.scalar(
            select(CategoryBenchmark).where(CategoryBenchmark.category == benchmark_data["category"])
        )
        if existing:
            continue
        db.add(CategoryBenchmark(**benchmark_data))
        created += 1
    db.flush()
    return created


def _seed_merchants(db: Session) -> tuple[int, int]:
    merchants_created = 0
    metrics_created = 0

    for merchant_seed in MERCHANTS:
        merchant = db.scalar(select(Merchant).where(Merchant.merchant_id == merchant_seed.merchant_id))
        if merchant is None:
            merchant = Merchant(
                merchant_id=merchant_seed.merchant_id,
                merchant_name=merchant_seed.merchant_name,
                category=merchant_seed.category,
                coupon_redemption_rate=merchant_seed.coupon_redemption_rate,
                unique_customer_count=merchant_seed.unique_customer_count,
                customer_return_rate=merchant_seed.customer_return_rate,
                avg_order_value=merchant_seed.avg_order_value,
                seasonality_index=merchant_seed.seasonality_index,
                deal_exclusivity_rate=merchant_seed.deal_exclusivity_rate,
                return_and_refund_rate=merchant_seed.return_and_refund_rate,
                registered_whatsapp_number=merchant_seed.registered_whatsapp_number,
                seed_intended_outcome=merchant_seed.seed_intended_outcome,
            )
            db.add(merchant)
            db.flush()
            merchants_created += 1
        elif merchant.registered_whatsapp_number != merchant_seed.registered_whatsapp_number:
            merchant.registered_whatsapp_number = merchant_seed.registered_whatsapp_number

        existing_months = set(
            db.scalars(
                select(MerchantMonthlyMetric.metric_month).where(MerchantMonthlyMetric.merchant_id == merchant.id)
            ).all()
        )
        for metric_seed in merchant_seed.monthly_metrics:
            if metric_seed.metric_month in existing_months:
                continue
            db.add(
                MerchantMonthlyMetric(
                    merchant_id=merchant.id,
                    metric_month=metric_seed.metric_month,
                    gmv=metric_seed.gmv,
                    orders_count=metric_seed.orders_count,
                    unique_customers=metric_seed.unique_customers,
                    refund_rate=metric_seed.refund_rate,
                )
            )
            metrics_created += 1

    db.flush()
    return merchants_created, metrics_created


def _seed_policy(db: Session) -> bool:
    existing = db.scalar(select(PolicyVersion).where(PolicyVersion.version_name == ACTIVE_POLICY["version_name"]))
    if existing:
        return False
    for policy in db.scalars(select(PolicyVersion).where(PolicyVersion.is_active.is_(True))).all():
        policy.is_active = False
    db.add(PolicyVersion(**ACTIVE_POLICY))
    db.flush()
    return True
