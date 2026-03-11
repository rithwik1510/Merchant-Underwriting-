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
    op.add_column(
        "merchants",
        sa.Column("registered_whatsapp_number", sa.String(length=30), nullable=True),
    )
    op.execute(
        "UPDATE merchants SET registered_whatsapp_number = 'whatsapp:+910000000000' "
        "WHERE registered_whatsapp_number IS NULL"
    )
    op.alter_column("merchants", "registered_whatsapp_number", nullable=False)


def downgrade() -> None:
    op.drop_column("merchants", "registered_whatsapp_number")
