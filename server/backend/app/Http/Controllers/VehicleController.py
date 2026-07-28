"""
Controller kendaraan — Server.
Hanya menampilkan data yang diterima dari node, tidak ada akses kamera/relay.
"""
from typing import Optional

from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.Http.Requests.VehicleRequest import (
    VehicleListOut,
    VehicleOut,
)
from app.Http.Requests.VehicleUpdateRequest import VehicleUpdateRequest
from app.Models.Vehicle import Vehicle


def search_vehicles(db: Session, q: str = "", limit: int = 20) -> list[dict]:
    """Search kendaraan by plat (untuk dropdown)."""
    from app.Models.VehicleOwner import VehicleOwner

    query = db.query(Vehicle).outerjoin(VehicleOwner, Vehicle.owner_id == VehicleOwner.id)
    if q:
        query = query.filter(Vehicle.plate_number.ilike(f"%{q}%"))
    query = query.order_by(Vehicle.plate_number)
    items = query.limit(limit).all()
    return [
        {
            "id": v.id,
            "plate_number": v.plate_number,
            "vehicle_type": v.vehicle_type,
            "cc": v.cc,
            "owner_id": v.owner_id,
            "owner_name": v.owner.owner_name if v.owner else None,
        }
        for v in items
    ]


def list_vehicles(db: Session, q: str = "", skip: int = 0, limit: int = 50) -> dict:
    """GET /api/vehicles — daftar kendaraan dengan pagination."""
    from app.Models.VehicleOwner import VehicleOwner

    query = db.query(Vehicle).outerjoin(VehicleOwner, Vehicle.owner_id == VehicleOwner.id)
    if q:
        query = query.filter(Vehicle.plate_number.ilike(f"%{q}%"))
    query = query.order_by(Vehicle.id.desc())
    total = query.count()
    print(f"[VEHICLES] list_vehicles: q='{q}' total={total}")
    items = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": v.id,
                "plate_number": v.plate_number,
                "vehicle_type": v.vehicle_type,
                "cc": v.cc,
                "owner_id": v.owner_id,
                "owner_name": v.owner.owner_name if v.owner else None,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in items
        ],
    }


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


def update_vehicle(db: Session, vehicle_id: int, request: VehicleUpdateRequest) -> dict:
    """PUT /api/vehicles/{id} — update tipe kendaraan & cc."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kendaraan tidak ditemukan",
        )

    if request.vehicle_type is not None:
        vehicle.vehicle_type = request.vehicle_type
    if request.cc is not None:
        vehicle.cc = request.cc

    db.commit()
    db.refresh(vehicle)

    return {
        "id": vehicle.id,
        "plate_number": vehicle.plate_number,
        "vehicle_type": vehicle.vehicle_type,
        "cc": vehicle.cc,
        "owner_id": vehicle.owner_id,
        "owner_name": vehicle.owner.owner_name if vehicle.owner else None,
        "updated_at": vehicle.updated_at.isoformat() if vehicle.updated_at else None,
    }


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
