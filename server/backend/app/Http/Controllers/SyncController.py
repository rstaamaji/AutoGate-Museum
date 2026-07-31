"""
Controller untuk sinkronisasi data dari node.

Node push event masuk/keluar → server simpan + cocokkan history.
Node tanya validasi plat → server cek apakah plat sedang di dalam.
Status node ditentukan dari aktivitas sync (last_seen_at), bukan heartbeat.
"""
import base64
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.Models.Vehicle import Vehicle
from app.Models.VehicleEvent import VehicleEvent
from app.Models.VehicleHistory import VehicleHistory
from app.Models.Node import Node


def _update_node_seen(db: Session, node_id: str):
    """Update last_seen_at dan status node setiap ada aktivitas sync."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if node:
        node.last_seen_at = datetime.now(timezone.utc)
        node.status = "online"


def receive_event(db: Session, payload: dict) -> dict:
    """
    Terima event masuk/keluar dari node.
    Payload:
        - event_id: UUID dari node
        - node_id: identifier node
        - plate_number: plat nomor
        - direction: "masuk" / "keluar"
        - plate_image_base64: gambar plat (opsional)
        - scene_image_base64: gambar scene (opsional)
        - confidence: tingkat kepercayaan (opsional)
        - captured_at: waktu capture (opsional)
        - rfid_uid: UID RFID (opsional)
        - is_update: True jika ini update RFID, bukan event baru
    """
    event_id = payload.get("event_id")
    node_id = payload.get("node_id")
    plate_number = payload.get("plate_number")
    direction = payload.get("direction")

    if not event_id or not node_id or not plate_number or not direction:
        raise HTTPException(status_code=400, detail="event_id, node_id, plate_number, direction wajib diisi")

    if direction not in ("masuk", "keluar"):
        raise HTTPException(status_code=400, detail="direction harus 'masuk' atau 'keluar'")

    # ── Handle update RFID ──
    if payload.get("is_update"):
        return _handle_rfid_update(db, event_id, payload.get("rfid_uid"))

    # Cek duplikat event_id
    existing = db.query(VehicleEvent).filter(VehicleEvent.event_id == event_id).first()
    if existing:
        return {"success": True, "event_id": event_id, "message": "Event sudah ada (duplikat)"}

    # Simpan gambar jika ada
    plate_image_path = None
    scene_image_path = None

    if payload.get("plate_image_base64"):
        plate_image_path = _save_base64_image(
            payload["plate_image_base64"],
            prefix=f"{node_id}_{direction}_plate",
        )

    if payload.get("scene_image_base64"):
        scene_image_path = _save_base64_image(
            payload["scene_image_base64"],
            prefix=f"{node_id}_{direction}_scene",
        )

    # Parse captured_at
    captured_at = None
    if payload.get("captured_at"):
        try:
            captured_at = datetime.fromisoformat(payload["captured_at"])
        except (ValueError, TypeError):
            captured_at = None

    # Auto-insert ke tabel vehicles jika plat belum ada
    try:
        existing_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
        if not existing_vehicle:
            # Cari owner_id dari tabel vehicle_owners jika ada
            from app.Models.VehicleOwner import VehicleOwner
            owner = db.query(VehicleOwner).filter(VehicleOwner.plate_number == plate_number).first()
            new_vehicle = Vehicle(plate_number=plate_number, owner_id=owner.id if owner else None)
            db.add(new_vehicle)
            db.flush()
            print(f"[SYNC] Vehicle baru: id={new_vehicle.id} plate={plate_number} owner_id={new_vehicle.owner_id}")
        else:
            # Jika vehicle ada tapi owner_id belum diisi, coba link
            if existing_vehicle.owner_id is None:
                from app.Models.VehicleOwner import VehicleOwner
                owner = db.query(VehicleOwner).filter(VehicleOwner.plate_number == plate_number).first()
                if owner:
                    existing_vehicle.owner_id = owner.id
                    print(f"[SYNC] Vehicle {plate_number} di-link ke owner_id={owner.id}")
            print(f"[SYNC] Vehicle sudah ada: id={existing_vehicle.id} plate={plate_number}")
    except Exception as e:
        print(f"[SYNC] GAGAL insert vehicle '{plate_number}': {e}")
        db.rollback()
        # Lanjutkan proses event meskipun insert vehicle gagal

    # Simpan event
    event = VehicleEvent(
        event_id=event_id,
        node_id=node_id,
        plate_number=plate_number,
        direction=direction,
        plate_image_path=plate_image_path,
        scene_image_path=scene_image_path,
        confidence=payload.get("confidence"),
        rfid_uid=payload.get("rfid_uid"),
        captured_at=captured_at,
    )
    db.add(event)
    db.flush()

    # Proses pencocokan history
    if direction == "masuk":
        _process_entry(db, event)
    else:  # keluar
        _process_exit(db, event)

    # Update node status (online + last_seen_at)
    _update_node_seen(db, node_id)

    db.commit()

    return {
        "success": True,
        "event_id": event_id,
        "message": f"Event {direction} plat '{plate_number}' dari node '{node_id}' diterima",
    }


def validate_plate(db: Session, plate_number: str, node_id: str = None) -> dict:
    """
    GET /api/sync/validate/{plate_number}
    Node tanya: apakah plat ini sedang di dalam?
    Return: valid=True jika ada history is_inside=True untuk plat ini.
    """
    # Update node status jika diketahui
    if node_id:
        _update_node_seen(db, node_id)

    history = (
        db.query(VehicleHistory)
        .filter(
            VehicleHistory.plate_number == plate_number,
            VehicleHistory.is_inside == True,
        )
        .order_by(VehicleHistory.created_at.desc())
        .first()
    )

    if history:
        return {
            "valid": True,
            "history_id": history.id,
            "plate_number": plate_number,
            "entry_at": history.entry_at.isoformat() if history.entry_at else None,
            "entry_node_id": history.entry_node_id,
        }

    return {
        "valid": False,
        "plate_number": plate_number,
        "message": "Plat tidak ditemukan atau sudah keluar",
    }


def _handle_rfid_update(db: Session, event_id: str, rfid_uid: str | None) -> dict:
    """Update rfid_uid pada event yang sudah ada + update VehicleHistory."""
    event = db.query(VehicleEvent).filter(VehicleEvent.event_id == event_id).first()
    if not event:
        return {"success": False, "event_id": event_id, "message": "Event tidak ditemukan untuk update RFID"}

    event.rfid_uid = rfid_uid

    # Update VehicleHistory juga
    if event.direction == "masuk":
        history = (
            db.query(VehicleHistory)
            .filter(VehicleHistory.entry_event_id == event_id)
            .first()
        )
        if history:
            history.entry_rfid = rfid_uid
    else:
        history = (
            db.query(VehicleHistory)
            .filter(VehicleHistory.exit_event_id == event_id)
            .first()
        )
        if history:
            history.exit_rfid = rfid_uid

    db.commit()

    return {
        "success": True,
        "event_id": event_id,
        "message": f"RFID '{rfid_uid}' berhasil di-update",
    }


def _process_entry(db: Session, event: VehicleEvent):
    """
    Proses event masuk:
    - Buat history baru dengan entry_event_id, is_inside=True.
    """
    history = VehicleHistory(
        entry_event_id=event.event_id,
        plate_number=event.plate_number,
        entry_node_id=event.node_id,
        entry_at=event.captured_at or event.created_at,
        entry_rfid=event.rfid_uid,
        is_inside=True,
    )
    db.add(history)


def _process_exit(db: Session, event: VehicleEvent):
    """
    Proses event keluar:
    - Cari history dengan plate_number sama dan is_inside=True.
    - Jika ketemu → update: exit_event_id, exit_node_id, exit_at, is_inside=False.
    - Jika tidak ketemu → tetap simpan event (data anomali).
    """
    history = (
        db.query(VehicleHistory)
        .filter(
            VehicleHistory.plate_number == event.plate_number,
            VehicleHistory.is_inside == True,
        )
        .order_by(VehicleHistory.created_at.desc())
        .first()
    )

    if history:
        history.exit_event_id = event.event_id
        history.exit_node_id = event.node_id
        history.exit_at = event.captured_at or event.created_at
        history.exit_rfid = event.rfid_uid
        history.is_inside = False


def _save_base64_image(b64_data: str, prefix: str) -> str:
    """Simpan gambar dari base64 ke storage."""
    filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
    filepath = Path(settings.STORAGE_DIR) / filename
    filepath.write_bytes(base64.b64decode(b64_data))
    return str(filepath)
