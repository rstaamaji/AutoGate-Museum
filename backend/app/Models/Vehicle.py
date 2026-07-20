"""
Mirip app/Models/Vehicle.php (Eloquent Model) di Laravel.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    direction = Column(String(10), index=True, nullable=False)  # "masuk" atau "keluar"
    plate_number = Column(String(20), index=True, nullable=False)
    plate_image_path = Column(String(255), nullable=True)       # foto crop plat nomor
    scene_image_path = Column(String(255), nullable=True)       # foto scene/kendaraan penuh
    confidence = Column(Float, nullable=True)                    # confidence hasil ANPR (%)
    captured_at = Column(DateTime, nullable=True)                 # waktu kamera mendeteksi plat
    created_at = Column(DateTime(timezone=True), server_default=func.now())
