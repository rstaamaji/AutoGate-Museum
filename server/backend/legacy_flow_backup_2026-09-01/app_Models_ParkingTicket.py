from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class ParkingTicket(Base):
    __tablename__ = "parking_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String(64), unique=True, nullable=False, index=True)
    barcode_token = Column(String(128), unique=True, nullable=False, index=True)

    plate_number = Column(String(20), nullable=False, index=True)
    entry_event_id = Column(String(36), nullable=True, index=True)
    exit_event_id = Column(String(36), nullable=True, index=True)
    entry_gate_opened_at = Column(DateTime, nullable=True)

    order_id = Column(String(100), unique=True, nullable=True, index=True)
    payment_token = Column(String(255), nullable=True)
    payment_redirect_url = Column(String(500), nullable=True)
    payment_created_at = Column(DateTime(timezone=True), nullable=True)
    amount = Column(Integer, nullable=False, default=5000)
    status = Column(String(30), nullable=False, default="pending")

    entry_at = Column(DateTime, nullable=True)
    exit_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    used_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())