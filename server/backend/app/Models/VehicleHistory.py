"""
Model VehicleHistory — record gabungan masuk + keluar.
1 record mewakili 1 siklus: kendaraan masuk lalu keluar.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class VehicleHistory(Base):
    __tablename__ = "vehicle_histories"

    id = Column(Integer, primary_key=True, index=True)
    entry_event_id = Column(String(36), nullable=True, index=True)  # FK → vehicle_events.event_id
    exit_event_id = Column(String(36), nullable=True, index=True)   # FK → vehicle_events.event_id
    plate_number = Column(String(20), nullable=False, index=True)
    entry_node_id = Column(String(50), nullable=True)
    exit_node_id = Column(String(50), nullable=True)
    entry_at = Column(DateTime, nullable=True)
    exit_at = Column(DateTime, nullable=True)
    entry_rfid = Column(String(100), nullable=True)
    exit_rfid = Column(String(100), nullable=True)
    is_inside = Column(Boolean, default=True)  # True=sedang di dalam, False=sudah keluar
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
