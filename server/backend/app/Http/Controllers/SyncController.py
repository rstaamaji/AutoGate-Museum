"""
Controller untuk menerima data sinkronisasi dari pos satpam (node).
"""
import base64
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.Models.Vehicle import Vehicle


def receive_vehicle_data(db: Session, payload: dict) -> dict:
    """
    Terima data kendaraan dari node.
    Payload berisi data plat + gambar (base64).
    """
    node_id = payload.get("node_id")
    if not node_id:
        raise HTTPException(status_code=400, detail="node_id wajib diisi")

    # Simpan gambar jika ada
    plate_image_path = None
    scene_image_path = None

    if payload.get("plate_image_base64"):
        plate_image_path = _save_base64_image(
            payload["plate_image_base64"],
            prefix=f"{node_id}_plate",
        )

    if payload.get("scene_image_base64"):
        scene_image_path = _save_base64_image(
            payload["scene_image_base64"],
            prefix=f"{node_id}_scene",
        )

    # Parse captured_at
    captured_at = None
    if payload.get("captured_at"):
        try:
            captured_at = datetime.fromisoformat(payload["captured_at"])
        except (ValueError, TypeError):
            captured_at = None

    vehicle = Vehicle(
        node_id=node_id,
        direction=payload.get("direction", ""),
        plate_number=payload.get("plate_number", ""),
        plate_image_path=plate_image_path,
        scene_image_path=scene_image_path,
        confidence=payload.get("confidence"),
        captured_at=captured_at,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return {
        "success": True,
        "vehicle_id": vehicle.id,
        "message": f"Data dari node '{node_id}' diterima",
    }


def _save_base64_image(b64_data: str, prefix: str) -> str:
    """Simpan gambar dari base64 ke storage."""
    filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
    filepath = Path(settings.STORAGE_DIR) / filename
    filepath.write_bytes(base64.b64decode(b64_data))
    return str(filepath)
