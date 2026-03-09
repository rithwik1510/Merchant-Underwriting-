"""phase3 explanations and whatsapp

Revision ID: 20260309_0003
Revises: 20260309_0002
Create Date: 2026-03-09 23:59:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260309_0003"
down_revision = "20260309_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_generations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("provider_name", sa.String(length=50), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("generation_type", sa.Enum("decision_explanation", "whatsapp_message", name="llmgenerationtype", native_enum=False), nullable=False),
        sa.Column("status", sa.Enum("success", "fallback", "failed_validation", "failed_provider", name="llmgenerationstatus", native_enum=False), nullable=False),
        sa.Column("input_payload_json", sa.JSON(), nullable=False),
        sa.Column("output_payload_json", sa.JSON(), nullable=False),
        sa.Column("validation_errors_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
        sa.Column("llm_generation_id", sa.Integer(), nullable=True),
        sa.Column("recipient_phone", sa.String(length=30), nullable=False),
        sa.Column("message_type", sa.Enum("credit_offer", "insurance_offer", "combined_offer", name="whatsappmessagetype", native_enum=False), nullable=False),
        sa.Column("content_text", sa.String(length=2000), nullable=False),
        sa.Column("twilio_message_sid", sa.String(length=100), nullable=True),
        sa.Column("delivery_status", sa.Enum("draft", "queued", "sent", "delivered", "failed", name="whatsappdeliverystatus", native_enum=False), nullable=False),
        sa.Column("provider_response_json", sa.JSON(), nullable=True),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["llm_generation_id"], ["llm_generations.id"]),
    )


def downgrade() -> None:
    op.drop_table("whatsapp_messages")
    op.drop_table("llm_generations")
