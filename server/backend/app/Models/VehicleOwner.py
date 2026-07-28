"""
Model VehicleOwner — data pemilik kendaraan berdasarkan plat nomor.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class VehicleOwner(Base):
    __tablename__ = "vehicle_owners"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    owner_name = Column(String(100), nullable=False)
    owner_address = Column(String(255), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
