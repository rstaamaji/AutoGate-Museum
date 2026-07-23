"""
Mirip app/Services/VehicleService.php — logika bisnis utama:
ambil data dari kamera (masuk/keluar) -> simpan gambar plat + scene ke disk
-> simpan record ke database. Kalau plat tidak terbaca ("unknown"), abaikan
(tidak disimpan ke DB).
"""
import uuid
from pathlib import Path
from typing import NamedTuple, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.Models.Vehicle import Vehicle
from app.Services import CameraService


class CaptureOutcome(NamedTuple):
    vehicle: Optional[Vehicle]
    ignored: bool
    reason: Optional[str]


def _save_image(image_bytes: bytes, prefix: str) -> str:
    filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
    filepath = Path(settings.STORAGE_DIR) / filename
    filepath.write_bytes(image_bytes)
    return str(filepath)


def _to_image_url(image_path: Optional[str]) -> Optional[str]:
    if not image_path:
        return None
    filename = Path(image_path).name
    return f"{settings.STORAGE_PUBLIC_PATH.rstrip('/')}/{filename}"


def capture_and_save(db: Session, direction: str, channel: Optional[int] = None) -> CaptureOutcome:
    """
    Trigger kamera sesuai arah ('masuk'/'keluar'), simpan foto plat + foto
    scene + data plat ke database. Dipanggil oleh POST /api/plates/{direction}.

    Kalau plat tidak terbaca (unknown/kosong), request diabaikan: tidak ada
    row baru yang dibuat, dan CaptureOutcome.ignored=True.
    """
    try:
        result = CameraService.capture_plate(direction, channel=channel)
    except CameraService.CameraError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Tidak bisa mengambil data dari kamera '{direction}': {e}",
        )

    if not result["is_known"]:
        return CaptureOutcome(
            vehicle=None,
            ignored=True,
            reason="Plat nomor tidak terbaca (unknown) — diabaikan, tidak disimpan.",
        )

    plate_image_path = None
    if result["plate_image_bytes"]:
        plate_image_path = _save_image(result["plate_image_bytes"], prefix=f"{direction}_plate")

    scene_image_path = None
    if result["scene_image_bytes"]:
        scene_image_path = _save_image(result["scene_image_bytes"], prefix=f"{direction}_scene")

    if not plate_image_path and not scene_image_path:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Kamera '{direction}' tidak mengirim gambar apa pun pada capture terakhir.",
        )

    vehicle = Vehicle(
        direction=direction,
        plate_number=result["plate"],
        plate_image_path=plate_image_path,
        scene_image_path=scene_image_path,
        confidence=result["confidence"],
        captured_at=result["captured_at"],
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return CaptureOutcome(vehicle=vehicle, ignored=False, reason=None)


def get_all(
    db: Session, skip: int = 0, limit: int = 100, direction: Optional[str] = None
) -> tuple[list[Vehicle], int]:
    """Dipanggil oleh GET /api/plates. Bisa difilter per arah lewat ?direction=masuk|keluar."""
    query = db.query(Vehicle)
    if direction:
        query = query.filter(Vehicle.direction == direction)
    query = query.order_by(Vehicle.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def to_out_dict(vehicle: Vehicle) -> dict:
    return {
        "id": vehicle.id,
        "direction": vehicle.direction,
        "plate_number": vehicle.plate_number,
        "plate_image_url": _to_image_url(vehicle.plate_image_path),
        "scene_image_url": _to_image_url(vehicle.scene_image_path),
        "confidence": vehicle.confidence,
        "captured_at": vehicle.captured_at,
        "created_at": vehicle.created_at,
    }
