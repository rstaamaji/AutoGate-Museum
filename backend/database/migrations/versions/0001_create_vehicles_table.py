"""create vehicles table

Revision ID: 0001
Revises:
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("plate_number", sa.String(length=20), nullable=False, index=True),
        sa.Column("image_path", sa.String(length=255), nullable=False),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("captured_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
