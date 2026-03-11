"""ai sanity check artifacts

Revision ID: 20260311_0006
Revises: 20260311_0005
Create Date: 2026-03-11 23:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260311_0006"
down_revision = "20260311_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "ai_sanity_checks" not in tables:
        op.create_table(
            "ai_sanity_checks",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("underwriting_run_id", sa.Integer(), nullable=False),
            sa.Column("provider_name", sa.String(length=50), nullable=False),
            sa.Column("model_name", sa.String(length=120), nullable=False),
            sa.Column(
                "status",
                sa.Enum("passed", "warning", "unavailable", "skipped", name="aisanitycheckstatus", native_enum=False),
                nullable=False,
            ),
            sa.Column("issue_codes_json", sa.JSON(), nullable=False),
            sa.Column("notes_json", sa.JSON(), nullable=False),
            sa.Column("suggested_explanation_focus_json", sa.JSON(), nullable=False),
            sa.Column("suggested_message_focus_json", sa.JSON(), nullable=False),
            sa.Column("input_payload_json", sa.JSON(), nullable=False),
            sa.Column("output_payload_json", sa.JSON(), nullable=False),
            sa.Column("validation_errors_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["underwriting_run_id"], ["underwriting_runs.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("underwriting_run_id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "ai_sanity_checks" in tables:
        op.drop_table("ai_sanity_checks")
