"""
Model VehicleEvent — catatan setiap kejadian masuk/keluar dari node.
1 event = 1 kali capture di 1 gate.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base


class VehicleEvent(Base):
    __tablename__ = "vehicle_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID dari node
    node_id = Column(String(50), nullable=False, index=True)
    plate_number = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False, index=True)  # masuk / keluar
    plate_image_path = Column(String(255), nullable=True)
    scene_image_path = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    captured_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # waktu diterima server
