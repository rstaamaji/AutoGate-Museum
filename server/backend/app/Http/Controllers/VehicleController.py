"""
Controller kendaraan — Server.
Hanya menampilkan data yang diterima dari node, tidak ada akses kamera/relay.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.Http.Requests.VehicleRequest import (
    VehicleListOut,
    VehicleOut,
)
from app.Models.Vehicle import Vehicle


def _to_image_url(image_path: Optional[str]) -> Optional[str]:
    if not image_path:
        return None
    from pathlib import Path
    from app.config import settings
    filename = Path(image_path).name
    return f"{settings.STORAGE_PUBLIC_PATH.rstrip('/')}/{filename}"


def index(db: Session, skip: int = 0, limit: int = 100, direction: Optional[str] = None, node_id: Optional[str] = None) -> VehicleListOut:
    """GET /api/vehicles — daftar kendaraan dari semua node."""
    query = db.query(Vehicle)
    if direction:
        query = query.filter(Vehicle.direction == direction)
    if node_id:
        query = query.filter(Vehicle.node_id == node_id)
    query = query.order_by(Vehicle.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return VehicleListOut(
        total=total,
        items=[_to_out(v) for v in items],
    )


def _to_out(v: Vehicle) -> VehicleOut:
    return VehicleOut(
        id=v.id,
        node_id=v.node_id,
        direction=v.direction,
        plate_number=v.plate_number,
        plate_image_url=_to_image_url(v.plate_image_path),
        scene_image_url=_to_image_url(v.scene_image_path),
        confidence=v.confidence,
        captured_at=v.captured_at.isoformat() if v.captured_at else None,
        created_at=v.created_at.isoformat() if v.created_at else None,
    )
