"""
Controller RFID — Pos Satpam.
Menerima input RFID setelah ANPR mendeteksi kendaraan.

Alur:
  1. Terima event_id + rfid_uid dari frontend
  2. Update vehicle record dengan rfid_uid
  3. Untuk keluar: cek kecocokan RFID dengan entry
  4. Buka gate
"""
import json
import logging

from app.database import get_db
from app.Models.Vehicle import Vehicle
from app.Http.Controllers.RelayController import RelayController

logger = logging.getLogger(__name__)


def _build_rfid_update_payload(vehicle: Vehicle, rfid_uid: str | None) -> dict:
    """Bangun payload untuk sync update RFID (data dasar + rfid_uid)."""
    from app.config import settings

    return {
        "event_id": vehicle.event_id,
        "node_id": settings.NODE_ID,
        "direction": vehicle.direction,
        "plate_number": vehicle.plate_number,
        "confidence": vehicle.confidence,
        "captured_at": vehicle.captured_at,
        "created_at": vehicle.created_at,
        "rfid_uid": rfid_uid,
        "is_update": True,  # Flag: ini update, bukan event baru
    }


def _check_rfid_match(plate_number: str, rfid_uid: str) -> bool | None:
    """
    Cek apakah RFID keluar cocok dengan RFID masuk untuk plat yang sama.

    Returns:
        True  — RFID cocok dengan entry terakhir
        False — RFID berbeda dengan entry terakhir
        None  — entry terakhir tidak punya RFID (tidak bisa dicocokkan)
    """
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT rfid_uid FROM vehicles
            WHERE plate_number = ? AND direction = 'masuk'
            ORDER BY created_at DESC LIMIT 1
            """,
            (plate_number,),
        ).fetchone()

    if not row:
        return None  # Tidak ada entry record

    entry_rfid = row["rfid_uid"]
    if not entry_rfid:
        return None  # Entry tanpa RFID

    return entry_rfid == rfid_uid


def handle_rfid(event_id: str, rfid_uid: str | None, background_tasks) -> dict:
    """
    POST /api/rfid — update vehicle dengan RFID, lalu buka gate.

    Args:
        event_id: UUID dari vehicle yang sudah di-capture
        rfid_uid: UID kartu RFID (null jika "Lanjutkan" tanpa RFID)
        background_tasks: FastAPI background tasks

    Returns:
        dict dengan success, message, rfid_match
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM vehicles WHERE event_id = ?", (event_id,)
        ).fetchone()

        if not row:
            return {"success": False, "message": f"Event '{event_id}' tidak ditemukan.", "rfid_match": None}

        vehicle = Vehicle.from_row(row)

        # Update rfid_uid
        conn.execute(
            "UPDATE vehicles SET rfid_uid = ? WHERE event_id = ?",
            (rfid_uid, event_id),
        )

        # Selalu buat sync_queue entry baru untuk update RFID
        # (menghindari race condition dengan sync service)
        if rfid_uid:
            new_payload = _build_rfid_update_payload(vehicle, rfid_uid)
            conn.execute(
                "INSERT INTO sync_queue (vehicle_id, payload, status) VALUES (?, ?, 'pending')",
                (vehicle.id, json.dumps(new_payload)),
            )

    # Cek kecocokan RFID untuk keluar
    rfid_match = None
    if vehicle.direction == "keluar" and rfid_uid:
        rfid_match = _check_rfid_match(vehicle.plate_number, rfid_uid)
        if rfid_match is False:
            logger.warning(
                f"RFID mismatch: plat '{vehicle.plate_number}' — "
                f"RFID keluar '{rfid_uid}' berbeda dengan entry"
            )
        elif rfid_match is True:
            logger.info(f"RFID match: plat '{vehicle.plate_number}' — RFID cocok")

    # Buka gate
    relay_channel = 1 if vehicle.direction == "masuk" else 4
    background_tasks.add_task(RelayController.open_and_close_delayed, relay_channel, 15)

    rfid_status = "dengan RFID" if rfid_uid else "tanpa RFID"
    logger.info(f"RFID: {vehicle.plate_number} ({vehicle.direction}) — gate dibuka {rfid_status}")

    return {
        "success": True,
        "message": f"Gate {vehicle.direction} dibuka {rfid_status}.",
        "rfid_match": rfid_match,
    }
