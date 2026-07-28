"""create vehicles table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-27

Tabel vehicles: data kendaraan (plat, tipe, cc, pemilik).
Dicatat otomatis saat sync dari node jika plat belum ada.
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("plate_number", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("vehicle_type", sa.String(50), nullable=True),
        sa.Column("cc", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("vehicle_owners.id"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
