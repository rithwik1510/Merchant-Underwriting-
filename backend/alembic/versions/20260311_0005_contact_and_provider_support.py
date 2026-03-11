"""merchant contacts and provider support

Revision ID: 20260311_0005
Revises: 20260310_0004
Create Date: 2026-03-11 15:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260311_0005"
down_revision = "20260310_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("merchants")}
    if "registered_whatsapp_number" not in columns:
        op.add_column(
            "merchants",
            sa.Column("registered_whatsapp_number", sa.String(length=30), nullable=True),
        )
    op.execute(
        "UPDATE merchants SET registered_whatsapp_number = 'whatsapp:+910000000000' "
        "WHERE registered_whatsapp_number IS NULL"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("merchants")}
    if "registered_whatsapp_number" in columns:
        op.drop_column("merchants", "registered_whatsapp_number")
