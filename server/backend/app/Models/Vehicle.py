"""
Model Vehicle — data kendaraan (plat, tipe, cc, pemilik).
Dicatat otomatis saat sync dari node jika plat belum ada.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_type = Column(String(50), nullable=True)   # mobil, motor, truk, dll
    cc = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("vehicle_owners.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("VehicleOwner", lazy="joined")
