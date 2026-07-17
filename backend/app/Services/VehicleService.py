"""
Mirip app/Services/VehicleService.php — logika bisnis utama:
ambil data dari kamera -> simpan gambar ke disk -> simpan record ke DB.
"""
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.Models.Vehicle import Vehicle
from app.Services import CameraService


def _save_image(image_bytes: bytes) -> str:
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = Path(settings.STORAGE_DIR) / filename
    filepath.write_bytes(image_bytes)
    return str(filepath)


def _to_image_url(image_path: str) -> str:
    filename = Path(image_path).name
    return f"{settings.STORAGE_PUBLIC_PATH.rstrip('/')}/{filename}"


def capture_and_save(db: Session, channel: Optional[int] = None) -> Vehicle:
    """Trigger kamera, simpan gambar + plat ke database. Dipanggil oleh POST /api/plates."""
    try:
        result = CameraService.capture_plate(channel=channel)
    except CameraService.CameraError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Tidak bisa mengambil data dari kamera: {e}",
        )

    if not result["plate"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kamera tidak mendeteksi plat nomor pada capture terakhir.",
        )

    if not result["image_bytes"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kamera tidak mengirim gambar pada capture terakhir.",
        )

    image_path = _save_image(result["image_bytes"])

    vehicle = Vehicle(
        plate_number=result["plate"],
        image_path=image_path,
        confidence=result["confidence"],
        captured_at=result["captured_at"],
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Vehicle], int]:
    """Dipanggil oleh GET /api/plates."""
    query = db.query(Vehicle).order_by(Vehicle.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def to_out_dict(vehicle: Vehicle) -> dict:
    return {
        "id": vehicle.id,
        "plate_number": vehicle.plate_number,
        "image_url": _to_image_url(vehicle.image_path),
        "confidence": vehicle.confidence,
        "captured_at": vehicle.captured_at,
        "created_at": vehicle.created_at,
    }
