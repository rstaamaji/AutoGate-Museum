"""
Mirip app/Http/Controllers/VehicleController.php — menerima request,
panggil Service, kembalikan response. Tidak ada logika bisnis di sini.
"""
from sqlalchemy.orm import Session

from app.Http.Requests.VehicleRequest import VehicleCaptureRequest, VehicleListOut, VehicleOut
from app.Services import VehicleService


def index(db: Session, skip: int = 0, limit: int = 100) -> VehicleListOut:
    """GET /api/plates — daftar semua plat yang pernah tercatat."""
    items, total = VehicleService.get_all(db, skip=skip, limit=limit)
    return VehicleListOut(
        total=total,
        items=[VehicleOut(**VehicleService.to_out_dict(v)) for v in items],
    )


def store(db: Session, payload: VehicleCaptureRequest) -> VehicleOut:
    """POST /api/plates — trigger kamera, simpan plat + gambar ke database."""
    vehicle = VehicleService.capture_and_save(db, channel=payload.channel)
    return VehicleOut(**VehicleService.to_out_dict(vehicle))
