"""two cameras (in/out) + license plate & scene picture

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # arah kamera: "masuk" / "keluar". Default sementara "masuk" untuk baris lama,
    # lalu kolom dibuat NOT NULL setelah backfill.
    op.add_column(
        "vehicles",
        sa.Column("direction", sa.String(length=10), nullable=False, server_default="masuk"),
    )
    op.create_index(op.f("ix_vehicles_direction"), "vehicles", ["direction"])
    op.alter_column("vehicles", "direction", server_default=None)

    # image_path lama -> plate_image_path (foto crop plat), sekarang boleh kosong
    op.alter_column(
        "vehicles",
        "image_path",
        new_column_name="plate_image_path",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    # foto scene / kendaraan penuh
    op.add_column("vehicles", sa.Column("scene_image_path", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("vehicles", "scene_image_path")
    op.alter_column(
        "vehicles",
        "plate_image_path",
        new_column_name="image_path",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.drop_index(op.f("ix_vehicles_direction"), table_name="vehicles")
    op.drop_column("vehicles", "direction")
