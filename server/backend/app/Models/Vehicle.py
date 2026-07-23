"""
Model Vehicle — Server.
Data kendaraan yang diterima dari pos satpam (node).
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), index=True, nullable=False)  # identifier pos satpam
    direction = Column(String(10), index=True, nullable=False)  # "masuk" / "keluar"
    plate_number = Column(String(20), index=True, nullable=False)
    plate_image_path = Column(String(255), nullable=True)
    scene_image_path = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    captured_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    synced_at = Column(DateTime(timezone=True), server_default=func.now())
