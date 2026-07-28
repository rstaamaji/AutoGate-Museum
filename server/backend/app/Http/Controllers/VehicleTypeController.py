"""
Controller untuk master data tipe kendaraan (VehicleType) CRUD.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.Http.Requests.VehicleTypeRequest import (
    VehicleTypeCreateRequest,
    VehicleTypeUpdateRequest,
    VehicleTypeOut,
    VehicleTypeListOut,
)
from app.Models.VehicleType import VehicleType


def list_types(db: Session) -> VehicleTypeListOut:
    """GET /api/vehicle-types — daftar semua tipe kendaraan."""
    items = db.query(VehicleType).order_by(VehicleType.name).all()
    return VehicleTypeListOut(
        total=len(items),
        items=[_to_out(t) for t in items],
    )


def create_type(db: Session, request: VehicleTypeCreateRequest) -> VehicleTypeOut:
    """POST /api/vehicle-types — tambah tipe kendaraan baru."""
    existing = db.query(VehicleType).filter(VehicleType.name == request.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tipe kendaraan '{request.name}' sudah ada",
        )

    obj = VehicleType(name=request.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


def update_type(db: Session, type_id: int, request: VehicleTypeUpdateRequest) -> VehicleTypeOut:
    """PUT /api/vehicle-types/{id} — ubah tipe kendaraan."""
    obj = db.query(VehicleType).filter(VehicleType.id == type_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipe kendaraan tidak ditemukan",
        )

    if request.name is not None:
        existing = db.query(VehicleType).filter(
            VehicleType.name == request.name,
            VehicleType.id != type_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tipe kendaraan '{request.name}' sudah ada",
            )
        obj.name = request.name
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


def delete_type(db: Session, type_id: int) -> dict:
    """DELETE /api/vehicle-types/{id} — hapus tipe kendaraan."""
    obj = db.query(VehicleType).filter(VehicleType.id == type_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipe kendaraan tidak ditemukan",
        )

    db.delete(obj)
    db.commit()
    return {"success": True}


def _to_out(t: VehicleType) -> VehicleTypeOut:
    return VehicleTypeOut(
        id=t.id,
        name=t.name,
        created_at=t.created_at.isoformat() if t.created_at else None,
        updated_at=t.updated_at.isoformat() if t.updated_at else None,
    )
