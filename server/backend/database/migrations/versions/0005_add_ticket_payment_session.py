"""add deferred payment fields to parking tickets

Revision ID: 0005
Revises: 64a61fdf3593
"""
from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "64a61fdf3593"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parking_tickets", sa.Column("payment_token", sa.String(length=255), nullable=True))
    op.add_column("parking_tickets", sa.Column("payment_redirect_url", sa.String(length=500), nullable=True))
    op.add_column("parking_tickets", sa.Column("payment_created_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("parking_tickets", "payment_created_at")
    op.drop_column("parking_tickets", "payment_redirect_url")
    op.drop_column("parking_tickets", "payment_token")