"""
Service logika bisnis kendaraan — Pos Satpam.

Gate masuk:
  1. Capture dari kamera masuk
  2. Generate UUID event_id
  3. Simpan ke SQLite lokal + sync queue
  4. Buka relay masuk

Gate keluar:
  1. Capture dari kamera keluar
  2. Tanya server: apakah plat ini sedang di dalam?
  3. Jika valid → simpan ke SQLite + sync queue, buka relay keluar
  4. Jika tidak valid → tolak, jangan buka gate
  5. Jika server offline → fallback cek SQLite lokal
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional

import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.database import get_db
from app.Models.Vehicle import Vehicle
from app.Services import CameraService


class CaptureOutcome(NamedTuple):
    vehicle: Optional[Vehicle]
    ignored: bool
    reason: Optional[str]
    validated: Optional[bool] = None  # True=valid, False=ditolak, None=tidak perlu validasi


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


def _auth_headers() -> dict:
    """Header autentikasi untuk komunikasi ke server."""
    headers = {"Content-Type": "application/json"}
    if settings.SERVER_API_KEY:
        headers["X-API-Key"] = settings.SERVER_API_KEY
    return headers


def capture_and_save(direction: str, channel: Optional[int] = None) -> CaptureOutcome:
    """
    Trigger kamera, simpan foto + data ke SQLite lokal,
    lalu masukkan ke antrian sinkronisasi.

    Untuk gate keluar: validasi ke server dulu sebelum buka gate.
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

    plate_number = result["plate"]
    event_id = str(uuid.uuid4())

    # Untuk gate keluar: validasi ke server
    if direction == "keluar":
        is_valid = _validate_plate_with_server(plate_number)
        if not is_valid:
            return CaptureOutcome(
                vehicle=None,
                ignored=True,
                reason=f"Plat '{plate_number}' tidak valid untuk keluar (tidak ditemukan di sistem atau sudah keluar).",
                validated=False,
            )

    # Simpan gambar
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
            INSERT INTO vehicles (event_id, direction, plate_number, plate_image_path, scene_image_path,
                                  confidence, captured_at, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                event_id,
                direction,
                plate_number,
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

    return CaptureOutcome(
        vehicle=vehicle,
        ignored=False,
        reason=None,
        validated=True if direction == "keluar" else None,
    )


def _validate_plate_with_server(plate_number: str) -> bool:
    """
    Tanya server: apakah plat ini sedang di dalam?
    Return True jika server bilang valid.
    Jika server offline → fallback ke SQLite lokal.
    """
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{settings.SERVER_URL}/api/sync/validate/{plate_number}",
                headers=_auth_headers(),
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("valid", False)
            return False
    except Exception:
        # Server offline → fallback ke SQLite lokal
        return _validate_plate_locally(plate_number)


def _validate_plate_locally(plate_number: str) -> bool:
    """
    Fallback: cek SQLite lokal apakah ada record masuk tanpa keluar
    (hanya berlaku jika masuk+keluar di node yang sama).
    """
    with get_db() as conn:
        # Cari record masuk terakhir untuk plat ini
        row = conn.execute(
            """
            SELECT id FROM vehicles
            WHERE plate_number = ? AND direction = 'masuk'
            ORDER BY created_at DESC LIMIT 1
            """,
            (plate_number,),
        ).fetchone()

        if not row:
            return False

        # Cek apakah sudah ada record keluar setelah record masuk ini
        entry_id = row["id"]
        exit_row = conn.execute(
            """
            SELECT id FROM vehicles
            WHERE plate_number = ? AND direction = 'keluar' AND id > ?
            LIMIT 1
            """,
            (plate_number, entry_id),
        ).fetchone()

        return exit_row is None  # True jika belum ada keluar


def _build_sync_payload(vehicle: Vehicle) -> dict:
    """Bangun payload JSON untuk dikirim ke server."""
    payload = {
        "event_id": vehicle.event_id,
        "node_id": settings.NODE_ID,
        "direction": vehicle.direction,
        "plate_number": vehicle.plate_number,
        "confidence": vehicle.confidence,
        "captured_at": vehicle.captured_at,
        "created_at": vehicle.created_at,
        "rfid_uid": vehicle.rfid_uid,
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


def get_all(
    skip: int = 0,
    limit: int = 100,
    direction: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple[list[Vehicle], int]:
    """Ambil data kendaraan dari SQLite dengan filter direction, search plat nomor, & range tanggal."""
    with get_db() as conn:
        query = "SELECT * FROM vehicles"
        count_query = "SELECT COUNT(*) FROM vehicles"
        where_clauses = []
        params = []

        if direction:
            where_clauses.append("direction = ?")
            params.append(direction)

        if search and search.strip():
            where_clauses.append("plate_number LIKE ?")
            params.append(f"%{search.strip()}%")

        if start_date:
            where_clauses.append("created_at >= ?")
            params.append(f"{start_date} 00:00:00" if " " not in start_date and "T" not in start_date else start_date)

        if end_date:
            where_clauses.append("created_at <= ?")
            params.append(f"{end_date} 23:59:59" if " " not in end_date and "T" not in end_date else end_date)

        if where_clauses:
            where_str = " WHERE " + " AND ".join(where_clauses)
            query += where_str
            count_query += where_str

        total = conn.execute(count_query, params).fetchone()[0]

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        query_params = list(params) + [limit, skip]

        rows = conn.execute(query, query_params).fetchall()
        items = [Vehicle.from_row(r) for r in rows]

    return items, total


def to_out_dict(vehicle: Vehicle) -> dict:
    return {
        "id": vehicle.id,
        "event_id": vehicle.event_id,
        "direction": vehicle.direction,
        "plate_number": vehicle.plate_number,
        "plate_image_url": _to_image_url(vehicle.plate_image_path),
        "scene_image_url": _to_image_url(vehicle.scene_image_path),
        "confidence": vehicle.confidence,
        "captured_at": vehicle.captured_at,
        "created_at": vehicle.created_at,
        "synced": bool(vehicle.synced),
        "rfid_uid": vehicle.rfid_uid,
    }
