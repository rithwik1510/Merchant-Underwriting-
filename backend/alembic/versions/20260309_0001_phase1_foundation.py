"""phase1 foundation

Revision ID: 20260309_0001
Revises:
Create Date: 2026-03-09 23:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260309_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "category_benchmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=50), nullable=False, unique=True),
        sa.Column("avg_refund_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("avg_customer_return_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("avg_order_value_low", sa.Numeric(12, 2), nullable=False),
        sa.Column("avg_order_value_high", sa.Numeric(12, 2), nullable=False),
        sa.Column("typical_seasonality_low", sa.Numeric(6, 2), nullable=False),
        sa.Column("typical_seasonality_high", sa.Numeric(6, 2), nullable=False),
        sa.Column("risk_adjustment_factor", sa.Numeric(4, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "merchants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("merchant_id", sa.String(length=50), nullable=False),
        sa.Column("merchant_name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("coupon_redemption_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("unique_customer_count", sa.Integer(), nullable=False),
        sa.Column("customer_return_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("avg_order_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("seasonality_index", sa.Numeric(6, 2), nullable=False),
        sa.Column("deal_exclusivity_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("return_and_refund_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("seed_intended_outcome", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("merchant_id"),
    )
    op.create_index("ix_merchants_category", "merchants", ["category"])
    op.create_index("ix_merchants_merchant_id", "merchants", ["merchant_id"])
    op.create_table(
        "merchant_monthly_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("metric_month", sa.Date(), nullable=False),
        sa.Column("gmv", sa.Numeric(14, 2), nullable=False),
        sa.Column("orders_count", sa.Integer(), nullable=False),
        sa.Column("unique_customers", sa.Integer(), nullable=False),
        sa.Column("refund_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("merchant_id", "metric_month", name="uq_merchant_month"),
    )
    op.create_table(
        "policy_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version_name", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("rules_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("version_name"),
    )


def downgrade() -> None:
    op.drop_table("policy_versions")
    op.drop_table("merchant_monthly_metrics")
    op.drop_index("ix_merchants_merchant_id", table_name="merchants")
    op.drop_index("ix_merchants_category", table_name="merchants")
    op.drop_table("merchants")
    op.drop_table("category_benchmarks")
