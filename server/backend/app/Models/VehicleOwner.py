"""
 data pengunjung berdasarkan kartu e-money (card_uid).
Nama class/tabel TIDAK diubah dulu (biar tidak merembet ke router/schema lain),
cukup field-nya yang disesuaikan. Rename nama bisa jadi step terpisah nanti.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class VehicleOwner(Base):
    __tablename__ = "vehicle_owners"

    id = Column(Integer, primary_key=True, index=True)

    # --- BARU: identitas utama sekarang berbasis kartu, bukan plat ---
    card_uid = Column(String(100), unique=True, nullable=False, index=True)

    # --- LAMA: plate_number, sekarang OPSIONAL (untuk kompatibilitas ke depan) ---
    plate_number = Column(String(20), unique=True, nullable=True, index=True)

    owner_name = Column(String(100), nullable=True)      # jadi opsional, museum bisa anonim
    owner_address = Column(String(255), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())