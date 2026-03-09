"""phase2 underwriting core

Revision ID: 20260309_0002
Revises: 20260309_0001
Create Date: 2026-03-09 23:45:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260309_0002"
down_revision = "20260309_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "underwriting_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("policy_version_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "COMPLETED", "REJECTED", "MANUAL_REVIEW", "FAILED", name="underwritingrunstatus", native_enum=False), nullable=False),
        sa.Column("decision", sa.Enum("approved", "manual_review", "rejected", name="underwritingdecision", native_enum=False), nullable=False),
        sa.Column("risk_tier", sa.Enum("tier_1", "tier_2", "tier_3", "rejected", name="risktier", native_enum=False), nullable=False),
        sa.Column("numeric_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("usable_history_months", sa.Integer(), nullable=False),
        sa.Column("hard_stop_triggered", sa.Boolean(), nullable=False),
        sa.Column("manual_review_triggered", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["policy_version_id"], ["policy_versions.id"]),
    )
    op.create_table(
        "feature_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("avg_monthly_gmv_3m", sa.Numeric(14, 2), nullable=True),
        sa.Column("annual_gmv_12m", sa.Numeric(14, 2), nullable=False),
        sa.Column("gmv_growth_3m_pct", sa.Numeric(8, 2), nullable=True),
        sa.Column("gmv_growth_12m_pct", sa.Numeric(8, 2), nullable=True),
        sa.Column("gmv_volatility_cv", sa.Numeric(8, 4), nullable=False),
        sa.Column("avg_orders_3m", sa.Numeric(12, 2), nullable=True),
        sa.Column("avg_unique_customers_3m", sa.Numeric(12, 2), nullable=True),
        sa.Column("customer_efficiency_ratio", sa.Numeric(14, 2), nullable=True),
        sa.Column("refund_delta_vs_category", sa.Numeric(8, 2), nullable=False),
        sa.Column("return_rate_delta_vs_category", sa.Numeric(8, 2), nullable=False),
        sa.Column("aov_position_vs_category_midpoint", sa.Numeric(12, 2), nullable=False),
        sa.Column("seasonality_pressure_score", sa.Numeric(4, 2), nullable=False),
        sa.Column("recent_gmv_drop_pct", sa.Numeric(8, 2), nullable=False),
        sa.Column("merchant_health_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("raw_feature_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("underwriting_run_id"),
    )
    op.create_table(
        "decision_reasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("reason_type", sa.Enum("hard_stop", "manual_review", "score_component", "offer_adjustment", name="decisionreasontype", native_enum=False), nullable=False),
        sa.Column("reason_code", sa.String(length=100), nullable=False),
        sa.Column("reason_label", sa.String(length=150), nullable=False),
        sa.Column("reason_detail", sa.String(length=500), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=True),
        sa.Column("metric_value", sa.Numeric(14, 4), nullable=True),
        sa.Column("benchmark_value", sa.Numeric(14, 4), nullable=True),
        sa.Column("weight", sa.Numeric(6, 2), nullable=True),
        sa.Column("impact_direction", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "credit_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("base_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("final_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("interest_rate_min", sa.Numeric(5, 2), nullable=True),
        sa.Column("interest_rate_max", sa.Numeric(5, 2), nullable=True),
        sa.Column("tenure_options_json", sa.JSON(), nullable=False),
        sa.Column("offer_status", sa.Enum("eligible", "manual_review", "not_offered", name="offerstatus", native_enum=False), nullable=False),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("underwriting_run_id"),
    )
    op.create_table(
        "insurance_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("coverage_base", sa.Numeric(14, 2), nullable=True),
        sa.Column("coverage_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("premium_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("premium_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("policy_type", sa.String(length=100), nullable=True),
        sa.Column("offer_status", sa.Enum("eligible", "manual_review", "not_offered", name="offerstatus", native_enum=False), nullable=False),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("underwriting_run_id"),
    )


def downgrade() -> None:
    op.drop_table("insurance_offers")
    op.drop_table("credit_offers")
    op.drop_table("decision_reasons")
    op.drop_table("feature_snapshots")
    op.drop_table("underwriting_runs")
