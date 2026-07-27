"""initial schema — reset total

Revision ID: 0001
Revises:
Create Date: 2026-07-27

Skema baru:
- users: autentikasi multi-role
- nodes: pos satpam dengan API key unik
- vehicle_owners: data pemilik kendaraan
- vehicle_events: catatan setiap kejadian masuk/keluar
- vehicle_histories: record gabungan masuk+keluar
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === users ===
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === nodes ===
    op.create_table(
        "nodes",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("api_key", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), server_default="offline"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("camera_in_active", sa.Boolean(), server_default="false"),
        sa.Column("camera_out_active", sa.Boolean(), server_default="false"),
        sa.Column("relay_in_active", sa.Boolean(), server_default="false"),
        sa.Column("relay_out_active", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === vehicle_owners ===
    op.create_table(
        "vehicle_owners",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("plate_number", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("owner_name", sa.String(100), nullable=False),
        sa.Column("owner_address", sa.String(255), nullable=True),
        sa.Column("owner_phone", sa.String(20), nullable=True),
        sa.Column("notes", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === vehicle_events ===
    op.create_table(
        "vehicle_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("node_id", sa.String(50), nullable=False, index=True),
        sa.Column("plate_number", sa.String(20), nullable=False, index=True),
        sa.Column("direction", sa.String(10), nullable=False, index=True),
        sa.Column("plate_image_path", sa.String(255), nullable=True),
        sa.Column("scene_image_path", sa.String(255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("captured_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === vehicle_histories ===
    op.create_table(
        "vehicle_histories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entry_event_id", sa.String(36), nullable=True, index=True),
        sa.Column("exit_event_id", sa.String(36), nullable=True, index=True),
        sa.Column("plate_number", sa.String(20), nullable=False, index=True),
        sa.Column("entry_node_id", sa.String(50), nullable=True),
        sa.Column("exit_node_id", sa.String(50), nullable=True),
        sa.Column("entry_at", sa.DateTime(), nullable=True),
        sa.Column("exit_at", sa.DateTime(), nullable=True),
        sa.Column("is_inside", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("vehicle_histories")
    op.drop_table("vehicle_events")
    op.drop_table("vehicle_owners")
    op.drop_table("nodes")
    op.drop_table("users")
