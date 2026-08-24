"""
Model VehicleHistory — record gabungan masuk + keluar.
1 record mewakili 1 siklus: pengunjung masuk lalu keluar.

PERUBAHAN dari versi asli:
- plate_number: NOT NULL -> nullable
- entry_rfid, exit_rfid: SUDAH ADA sebelumnya, sekarang jadi field utama
- BARU: kolom-kolom pembayaran Midtrans (status_bayar, midtrans_order_id,
  midtrans_transaction_id, jumlah_bayar), diisi saat proses keluar
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.sql import func

from app.database import Base


class VehicleHistory(Base):
    __tablename__ = "vehicle_histories"

    id = Column(Integer, primary_key=True, index=True)
    entry_event_id = Column(String(36), nullable=True, index=True)  # FK -> vehicle_events.event_id
    exit_event_id = Column(String(36), nullable=True, index=True)   # FK -> vehicle_events.event_id

    # --- DIUBAH: nullable=True (dulu nullable=False) ---
    plate_number = Column(String(20), nullable=True, index=True)

    entry_node_id = Column(String(50), nullable=True)
    exit_node_id = Column(String(50), nullable=True)
    entry_at = Column(DateTime, nullable=True)
    exit_at = Column(DateTime, nullable=True)

    # --- sudah ada sebelumnya, sekarang jadi cara utama identifikasi ---
    entry_rfid = Column(String(100), nullable=True)
    exit_rfid = Column(String(100), nullable=True)

    is_inside = Column(Boolean, default=True)  # True=sedang di dalam, False=sudah keluar

    # --- BARU: field pembayaran Midtrans ---
    status_bayar = Column(String(20), nullable=False, server_default="belum_bayar")
    # nilai: belum_bayar / pending / lunas / gagal
    midtrans_order_id = Column(String(100), nullable=True, index=True)
    midtrans_transaction_id = Column(String(100), nullable=True)
    jumlah_bayar = Column(Numeric(12, 2), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())