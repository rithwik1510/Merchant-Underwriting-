"""phase4 acceptance and mandates

Revision ID: 20260310_0004
Revises: 20260309_0003
Create Date: 2026-03-10 00:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260310_0004"
down_revision = "20260309_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offer_acceptances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("accepted_product_type", sa.Enum("credit", "insurance", "combined", name="acceptedproducttype", native_enum=False), nullable=False),
        sa.Column("accepted_by_name", sa.String(length=120), nullable=False),
        sa.Column("accepted_phone", sa.String(length=30), nullable=False),
        sa.Column("accepted_via", sa.Enum("dashboard", "whatsapp", "api", name="acceptancevia", native_enum=False), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acceptance_notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("underwriting_run_id"),
    )
    op.create_table(
        "mock_nach_mandates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("offer_acceptance_id", sa.Integer(), nullable=False),
        sa.Column("mandate_status", sa.Enum("initiated", "bank_selected", "otp_sent", "otp_verified", "umrn_generated", "completed", "failed", name="mandatestatus", native_enum=False), nullable=False),
        sa.Column("bank_name", sa.String(length=100), nullable=True),
        sa.Column("account_holder_name", sa.String(length=120), nullable=False),
        sa.Column("account_number_masked", sa.String(length=50), nullable=True),
        sa.Column("ifsc_masked", sa.String(length=20), nullable=True),
        sa.Column("mobile_number", sa.String(length=30), nullable=False),
        sa.Column("otp_code_hash", sa.String(length=200), nullable=True),
        sa.Column("otp_last_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("otp_attempt_count", sa.Integer(), nullable=False),
        sa.Column("umrn", sa.String(length=50), nullable=True),
        sa.Column("mandate_reference", sa.String(length=100), nullable=True),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["offer_acceptance_id"], ["offer_acceptances.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("underwriting_run_id"),
    )


def downgrade() -> None:
    op.drop_table("mock_nach_mandates")
    op.drop_table("offer_acceptances")
