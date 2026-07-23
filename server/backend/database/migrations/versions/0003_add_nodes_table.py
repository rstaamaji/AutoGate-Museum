"""add nodes table + node_id to vehicles

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-23

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Buat tabel nodes
    op.create_table(
        "nodes",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="offline"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("camera_in_active", sa.Boolean, server_default="false"),
        sa.Column("camera_out_active", sa.Boolean, server_default="false"),
        sa.Column("relay_in_active", sa.Boolean, server_default="false"),
        sa.Column("relay_out_active", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tambah kolom node_id ke vehicles
    op.add_column(
        "vehicles",
        sa.Column("node_id", sa.String(length=50), nullable=False, server_default="unknown"),
    )
    op.create_index(op.f("ix_vehicles_node_id"), "vehicles", ["node_id"])
    op.alter_column("vehicles", "node_id", server_default=None)

    # Tambah kolom synced_at
    op.add_column(
        "vehicles",
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_column("vehicles", "synced_at")
    op.drop_index(op.f("ix_vehicles_node_id"), table_name="vehicles")
    op.drop_column("vehicles", "node_id")
    op.drop_table("nodes")
