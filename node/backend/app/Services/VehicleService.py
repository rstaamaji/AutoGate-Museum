"""
Service logika bisnis kendaraan — Pos Satpam.
Simpan ke SQLite lokal + masukkan ke antrian sinkronisasi.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional

from fastapi import HTTPException, status

from app.config import settings
from app.database import get_db
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


def capture_and_save(direction: str, channel: Optional[int] = None) -> CaptureOutcome:
    """
    Trigger kamera, simpan foto + data ke SQLite lokal,
    lalu masukkan ke antrian sinkronisasi.
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
            detail=f"Kamera '{direction}' tidak mengirim gambar apa pun.",
        )

    # Simpan ke SQLite
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO vehicles (direction, plate_number, plate_image_path, scene_image_path,
                                  confidence, captured_at, synced)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                direction,
                result["plate"],
                plate_image_path,
                scene_image_path,
                result["confidence"],
                result["captured_at"].isoformat() if result["captured_at"] else None,
            ),
        )
        vehicle_id = cursor.lastrowid

        # Ambil data yang baru disimpan
        row = conn.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
        vehicle = Vehicle.from_row(row)

        # Masukkan ke antrian sinkronisasi
        sync_payload = _build_sync_payload(vehicle)
        conn.execute(
            """
            INSERT INTO sync_queue (vehicle_id, payload, status)
            VALUES (?, ?, 'pending')
            """,
            (vehicle_id, json.dumps(sync_payload)),
        )

    return CaptureOutcome(vehicle=vehicle, ignored=False, reason=None)


def _build_sync_payload(vehicle: Vehicle) -> dict:
    """Bangun payload JSON untuk dikirim ke server."""
    payload = {
        "node_id": settings.NODE_ID,
        "direction": vehicle.direction,
        "plate_number": vehicle.plate_number,
        "confidence": vehicle.confidence,
        "captured_at": vehicle.captured_at,
        "created_at": vehicle.created_at,
    }

    # Encode gambar sebagai base64 jika ada
    if vehicle.plate_image_path and Path(vehicle.plate_image_path).exists():
        import base64
        with open(vehicle.plate_image_path, "rb") as f:
            payload["plate_image_base64"] = base64.b64encode(f.read()).decode("utf-8")

    if vehicle.scene_image_path and Path(vehicle.scene_image_path).exists():
        import base64
        with open(vehicle.scene_image_path, "rb") as f:
            payload["scene_image_base64"] = base64.b64encode(f.read()).decode("utf-8")

    return payload


def get_all(skip: int = 0, limit: int = 100, direction: Optional[str] = None) -> tuple[list[Vehicle], int]:
    """Ambil semua data kendaraan dari SQLite."""
    with get_db() as conn:
        query = "SELECT * FROM vehicles"
        count_query = "SELECT COUNT(*) FROM vehicles"
        params = []

        if direction:
            query += " WHERE direction = ?"
            count_query += " WHERE direction = ?"
            params.append(direction)

        total = conn.execute(count_query, params).fetchone()[0]

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        rows = conn.execute(query, params).fetchall()
        items = [Vehicle.from_row(r) for r in rows]

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
        "synced": bool(vehicle.synced),
    }
