"""
Mirip app/Http/Controllers/VehicleController.php — menerima request,
panggil Service, kembalikan response. Tidak ada logika bisnis di sini.
"""
from typing import Optional

from fastapi import BackgroundTasks

from sqlalchemy.orm import Session

from app.Http.Requests.VehicleRequest import (
    VehicleCaptureOut,
    VehicleCaptureRequest,
    VehicleListOut,
    VehicleOut,
)
from app.Services import VehicleService
from app.Http.Controllers.RelayController import RelayController


def index(db: Session, skip: int = 0, limit: int = 100, direction: Optional[str] = None) -> VehicleListOut:
    """GET /api/plates — daftar semua plat yang pernah tercatat (bisa difilter ?direction=)."""
    items, total = VehicleService.get_all(db, skip=skip, limit=limit, direction=direction)
    return VehicleListOut(
        total=total,
        items=[VehicleOut(**VehicleService.to_out_dict(v)) for v in items],
    )


def store(db: Session, direction: str, payload: VehicleCaptureRequest, background_tasks: BackgroundTasks) -> VehicleCaptureOut:
    """POST /api/plates/{direction} — trigger kamera masuk/keluar, simpan plat + 2 gambar.
    Kalau plat tidak terbaca (unknown), request diabaikan (tidak disimpan)."""
    outcome = VehicleService.capture_and_save(db, direction=direction, channel=payload.channel)
    
    # Jika berhasil terbaca & tersimpan di DB
    if not outcome.ignored and outcome.vehicle:
        # Default asumsikan masuk = channel 1, keluar = channel 2
        relay_channel = 1 if direction == "masuk" else 2
        background_tasks.add_task(RelayController.open_and_close_delayed, relay_channel, 15)
        
    return VehicleCaptureOut(
        ignored=outcome.ignored,
        reason=outcome.reason,
        vehicle=VehicleOut(**VehicleService.to_out_dict(outcome.vehicle)) if outcome.vehicle else None,
    )
