"""drop description from vehicle_types

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-28

Menghapus kolom description dari tabel vehicle_types.
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("vehicle_types", "description")


def downgrade() -> None:
    op.add_column("vehicle_types", sa.Column("description", sa.String(255), nullable=True))
