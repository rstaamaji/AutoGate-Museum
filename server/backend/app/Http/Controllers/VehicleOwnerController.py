"""
Controller untuk CRUD pemilik kendaraan.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.Models.VehicleOwner import VehicleOwner
from app.Http.Requests.VehicleOwnerRequest import (
    VehicleOwnerCreateRequest,
    VehicleOwnerUpdateRequest,
    VehicleOwnerOut,
    VehicleOwnerListOut,
)


def _to_out(owner: VehicleOwner) -> VehicleOwnerOut:
    return VehicleOwnerOut(
        id=owner.id,
        plate_number=owner.plate_number,
        owner_name=owner.owner_name,
        owner_address=owner.owner_address,
        owner_phone=owner.owner_phone,
        notes=owner.notes,
        created_at=owner.created_at.isoformat() if owner.created_at else None,
        updated_at=owner.updated_at.isoformat() if owner.updated_at else None,
    )


def list_owners(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    plate_number: Optional[str] = None,
) -> VehicleOwnerListOut:
    """GET /api/vehicle-owners — daftar pemilik, optional filter plat."""
    query = db.query(VehicleOwner)
    if plate_number:
        query = query.filter(VehicleOwner.plate_number.ilike(f"%{plate_number}%"))
    query = query.order_by(VehicleOwner.id.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return VehicleOwnerListOut(total=total, items=[_to_out(o) for o in items])


def create_owner(db: Session, request: VehicleOwnerCreateRequest) -> VehicleOwnerOut:
    """POST /api/vehicle-owners — tambah pemilik."""
    # Cek plat unik
    existing = db.query(VehicleOwner).filter(VehicleOwner.plate_number == request.plate_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plat nomor '{request.plate_number}' sudah terdaftar",
        )

    owner = VehicleOwner(
        plate_number=request.plate_number,
        owner_name=request.owner_name,
        owner_address=request.owner_address,
        owner_phone=request.owner_phone,
        notes=request.notes,
    )
    db.add(owner)
    db.flush()

    # Link ke vehicle jika sudah ada
    from app.Models.Vehicle import Vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == request.plate_number).first()
    if vehicle and vehicle.owner_id is None:
        vehicle.owner_id = owner.id

    db.commit()
    db.refresh(owner)
    return _to_out(owner)


def update_owner(db: Session, owner_id: int, request: VehicleOwnerUpdateRequest) -> VehicleOwnerOut:
    """PUT /api/vehicle-owners/{id} — update pemilik."""
    from app.Models.Vehicle import Vehicle

    owner = db.query(VehicleOwner).filter(VehicleOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pemilik tidak ditemukan")

    old_plate = owner.plate_number

    if request.plate_number is not None:
        existing = db.query(VehicleOwner).filter(
            VehicleOwner.plate_number == request.plate_number,
            VehicleOwner.id != owner_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plat nomor '{request.plate_number}' sudah terdaftar",
            )
        owner.plate_number = request.plate_number

        # Unlink vehicle lama
        old_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == old_plate, Vehicle.owner_id == owner_id).first()
        if old_vehicle:
            old_vehicle.owner_id = None

        # Link vehicle baru
        new_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == request.plate_number).first()
        if new_vehicle and new_vehicle.owner_id is None:
            new_vehicle.owner_id = owner_id

    if request.owner_name is not None:
        owner.owner_name = request.owner_name
    if request.owner_address is not None:
        owner.owner_address = request.owner_address
    if request.owner_phone is not None:
        owner.owner_phone = request.owner_phone
    if request.notes is not None:
        owner.notes = request.notes

    db.commit()
    db.refresh(owner)
    return _to_out(owner)


def delete_owner(db: Session, owner_id: int) -> dict:
    """DELETE /api/vehicle-owners/{id} — hapus pemilik."""
    from app.Models.Vehicle import Vehicle

    owner = db.query(VehicleOwner).filter(VehicleOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pemilik tidak ditemukan")

    # Unlink vehicle yang terkait
    vehicle = db.query(Vehicle).filter(Vehicle.owner_id == owner_id).first()
    if vehicle:
        vehicle.owner_id = None

    db.delete(owner)
    db.commit()
    return {"success": True, "message": f"Pemilik plat '{owner.plate_number}' berhasil dihapus"}
