"""
Mirip app/Http/Controllers/VehicleController.php — menerima request,
panggil Service, kembalikan response. Tidak ada logika bisnis di sini.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.Http.Requests.VehicleRequest import (
    VehicleCaptureOut,
    VehicleCaptureRequest,
    VehicleListOut,
    VehicleOut,
)
from app.Services import VehicleService


def index(db: Session, skip: int = 0, limit: int = 100, direction: Optional[str] = None) -> VehicleListOut:
    """GET /api/plates — daftar semua plat yang pernah tercatat (bisa difilter ?direction=)."""
    items, total = VehicleService.get_all(db, skip=skip, limit=limit, direction=direction)
    return VehicleListOut(
        total=total,
        items=[VehicleOut(**VehicleService.to_out_dict(v)) for v in items],
    )


def store(db: Session, direction: str, payload: VehicleCaptureRequest) -> VehicleCaptureOut:
    """POST /api/plates/{direction} — trigger kamera masuk/keluar, simpan plat + 2 gambar.
    Kalau plat tidak terbaca (unknown), request diabaikan (tidak disimpan)."""
    outcome = VehicleService.capture_and_save(db, direction=direction, channel=payload.channel)
    return VehicleCaptureOut(
        ignored=outcome.ignored,
        reason=outcome.reason,
        vehicle=VehicleOut(**VehicleService.to_out_dict(outcome.vehicle)) if outcome.vehicle else None,
    )
