"""
Model VehicleType — master data tipe kendaraan.
Berisi daftar tipe kendaraan yang terkelola (mobil, motor, truk, dll).
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
