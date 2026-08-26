"""
Controller untuk menerima data dari kamera Hikvision ISAPI.
Kamera mengirim event via multipart/form-data dengan XML (tanpa gambar).

Alur:
  1. Parse multipart body dari kamera → ambil XML
  2. Extract dari XML: plate, confidence, timestamp, ipAddress
  3. Cocokkan IP → direction (masuk/keluar)
  4. Pull gambar dari kamera (plate image + scene image)
  5. Simpan ke SQLite + queue sync
    6. Gate keluar dibuka setelah barcode valid; gate masuk menunggu pembayaran
"""
import asyncio
import json
import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Request, status

from app.config import settings
from app.database import get_db
from app.Models.Vehicle import Vehicle
from app.Http.Requests.VehicleRequest import VehicleCaptureOut, VehicleOut
from app.Http.Requests.VehicleRequest import PaymentInfo
from app.Services import PaymentService
from app.Services import CameraService
from app.Services.VehicleService import to_out_dict

logger = logging.getLogger(__name__)


def _strip_ns(root: ET.Element):
    """Hapus namespace dari tag XML."""
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]
    return root


def _parse_multipart(body: bytes, content_type: str) -> dict[str, bytes]:
    """Parse multipart body, return dict {name: bytes}."""
    from requests_toolbelt.multipart import decoder as mt_decoder

    try:
        multipart = mt_decoder.MultipartDecoder(body, content_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal parse multipart body: {e}",
        )

    parts: dict[str, bytes] = {}
    for part in multipart.parts:
        disposition = part.headers.get(b"Content-Disposition", b"").decode(errors="ignore")
        name = None
        for chunk in disposition.split(";"):
            chunk = chunk.strip()
            if chunk.startswith("name="):
                name = chunk.split("=", 1)[1].strip('"')
                break
        parts[name or f"part_{len(parts)}"] = part.content

    return parts


def _find_xml_part(parts: dict[str, bytes]) -> Optional[bytes]:
    """Cari part yang berisi XML."""
    for name, content in parts.items():
        if "xml" in name.lower():
            return content
    for content in parts.values():
        try:
            ET.fromstring(content)
            return content
        except ET.ParseError:
            continue
    return None


def _extract_from_xml(xml_bytes: bytes) -> dict:
    """Extract plate, confidence, timestamp, ipAddress dari XML Hikvision."""
    root = ET.fromstring(xml_bytes)
    _strip_ns(root)

    plate = None
    for tag in ("licensePlate", "plateNumber", "plate"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text and elem.text.strip():
            plate = elem.text.strip()
            break

    confidence = None
    for tag in ("confidenceLevel", "confidence", "confidenceValue"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text:
            try:
                confidence = float(elem.text.strip())
            except ValueError:
                pass
            if confidence is not None:
                break

    captured_at = None
    for tag in ("dateTime", "captureTime", "timestamp"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text:
            raw = elem.text.strip()
            try:
                captured_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                pass
            if captured_at is not None:
                break

    ip_address = None
    for tag in ("ipAddress", "ip", "deviceIP"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text and elem.text.strip():
            ip_address = elem.text.strip()
            break

    return {
        "plate": plate,
        "confidence": confidence,
        "captured_at": captured_at,
        "ip_address": ip_address,
    }


def _save_image(image_bytes: bytes, prefix: str) -> str:
    """Simpan gambar ke storage, return path."""
    filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
    filepath = Path(settings.STORAGE_DIR) / filename
    filepath.write_bytes(image_bytes)
    return str(filepath)


def _is_unknown_plate(plate: Optional[str]) -> bool:
    if not plate or not plate.strip():
        return True
    return plate.strip().lower() in settings.UNKNOWN_PLATE_VALUES


def _pull_images_from_camera(direction: str) -> tuple[Optional[bytes], Optional[bytes]]:
    """
    Pull gambar terakhir dari kamera (plate image + scene image).
    Return (plate_image_bytes, scene_image_bytes).
    Jika gagal, return (None, None) — bukan exception.
    """
    try:
        result = CameraService.capture_plate(direction)
        return result.get("plate_image_bytes"), result.get("scene_image_bytes")
    except Exception as e:
        logger.warning(f"Gagal pull gambar dari kamera '{direction}': {e}")
        return None, None


def _validate_plate(plate_number: str) -> bool:
    """Validasi plat untuk gate keluar (cek ke server atau lokal)."""
    import httpx

    headers = {"Content-Type": "application/json"}
    if settings.SERVER_API_KEY:
        headers["X-API-Key"] = settings.SERVER_API_KEY

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{settings.SERVER_URL}/api/sync/validate/{plate_number}",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("valid", False)
            return False
    except Exception:
        return _validate_plate_locally(plate_number)


def _validate_plate_locally(plate_number: str) -> bool:
    """Fallback: cek SQLite lokal apakah ada record masuk tanpa keluar."""
    with get_db() as conn:
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

        entry_id = row["id"]
        exit_row = conn.execute(
            """
            SELECT id FROM vehicles
            WHERE plate_number = ? AND direction = 'keluar' AND id > ?
            LIMIT 1
            """,
            (plate_number, entry_id),
        ).fetchone()

        return exit_row is None


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

    if vehicle.plate_image_path and Path(vehicle.plate_image_path).exists():
        import base64
        with open(vehicle.plate_image_path, "rb") as f:
            payload["plate_image_base64"] = base64.b64encode(f.read()).decode("utf-8")

    if vehicle.scene_image_path and Path(vehicle.scene_image_path).exists():
        import base64
        with open(vehicle.scene_image_path, "rb") as f:
            payload["scene_image_base64"] = base64.b64encode(f.read()).decode("utf-8")

    return payload


async def handle_radar_event(request: Request, forced_direction: Optional[str] = None) -> VehicleCaptureOut:
    """
    POST /api/hikvision/radar — terima event dari kamera Hikvision ISAPI.

    1. Parse XML push → plat, confidence, timestamp, IP
    2. Pull gambar dari kamera (async, dengan retry)
    3. Simpan ke SQLite + queue sync + buka gate
    """
    # ── 1. Baca multipart body ──
    content_type = request.headers.get("content-type", "")
    if "multipart" not in content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type harus multipart/form-data dari kamera Hikvision.",
        )

    body = await request.body()
    parts = _parse_multipart(body, content_type)

    # ── 2. Parse XML ──
    xml_bytes = _find_xml_part(parts)
    if not xml_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak ditemukan bagian XML dalam request dari kamera.",
        )

    info = _extract_from_xml(xml_bytes)
    camera_ip = info["ip_address"]

    if not camera_ip and not forced_direction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag <ipAddress> tidak ditemukan atau kosong dalam XML.",
        )

    logger.info(f"Hikvision event dari IP: {camera_ip}")

    # ── 3. Cocokkan IP → direction ──
    if forced_direction:
        direction = forced_direction
    else:
        ip_in = settings.CAMERA_IN_HOST.strip()
        ip_out = settings.CAMERA_OUT_HOST.strip()

        if camera_ip == ip_in:
            direction = "masuk"
        elif camera_ip == ip_out:
            direction = "keluar"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"IP kamera '{camera_ip}' tidak dikenal. "
                       f"Expected IN={ip_in} atau OUT={ip_out}.",
            )

    logger.info(f"Direction ditentukan: {direction} (IP: {camera_ip})")

    # ── 4. Cek plat ──
    plate_number = info["plate"]
    is_known = not _is_unknown_plate(plate_number)

    if not is_known:
        return VehicleCaptureOut(
            ignored=True,
            reason="Plat nomor tidak terbaca (unknown) — diabaikan, tidak disimpan.",
        )

    # ── 5. Validasi untuk gate keluar ──
    if direction == "keluar":
        is_valid = _validate_plate(plate_number)
        if not is_valid:
            return VehicleCaptureOut(
                ignored=True,
                reason=f"Plat '{plate_number}' tidak valid untuk keluar.",
                validated=False,
            )

    # ── 6. Pull gambar dari kamera (dengan retry) ──
    plate_image_bytes = None
    scene_image_bytes = None

    for attempt in range(3):
        plate_image_bytes, scene_image_bytes = await asyncio.to_thread(
            _pull_images_from_camera, direction
        )
        if plate_image_bytes or scene_image_bytes:
            break
        if attempt < 2:
            logger.info(f"Retry pull gambar ({attempt + 2}/3)...")
            await asyncio.sleep(0.5)

    # Simpan gambar
    plate_image_path = None
    if plate_image_bytes:
        plate_image_path = _save_image(plate_image_bytes, prefix=f"{direction}_plate")

    scene_image_path = None
    if scene_image_bytes:
        scene_image_path = _save_image(scene_image_bytes, prefix=f"{direction}_scene")

    if not plate_image_path and not scene_image_path:
        logger.warning(f"Gagal pull gambar setelah 3 percobaan — simpan tanpa gambar.")

    # ── 7. Simpan ke SQLite + queue sync ──
    event_id = str(uuid.uuid4())
    captured_at = info["captured_at"].isoformat() if info["captured_at"] else None

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO vehicles (event_id, direction, plate_number, plate_image_path, scene_image_path,
                                  confidence, captured_at, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (event_id, direction, plate_number, plate_image_path, scene_image_path,
             info["confidence"], captured_at),
        )
        vehicle_id = cursor.lastrowid

        row = conn.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
        vehicle = Vehicle.from_row(row)

        sync_payload = _build_sync_payload(vehicle)
        conn.execute(
            "INSERT INTO sync_queue (vehicle_id, payload, status) VALUES (?, ?, 'pending')",
            (vehicle_id, json.dumps(sync_payload)),
        )

<<<<<<< Updated upstream
    # ── 8. Jangan buka gate dulu — tunggu RFID ──
    logger.info(f"Hikvision: {plate_number} ({direction}) disimpan, menunggu RFID")
=======
    payment = None

    # Gate masuk menunggu pembayaran; hanya gate keluar yang dibuka di jalur ini.
    if direction == "keluar":
        background_tasks.add_task(
            RelayController.open_and_close_delayed,
            4,
            15,
        )
        logger.info(f"Hikvision: {plate_number} ({direction}) disimpan, gate dibuka")
    else:
        payment = PaymentService.start_entry_payment(
            plate_number=vehicle.plate_number,
            entry_event_id=vehicle.event_id,
        )
        logger.info(
            f"Hikvision: {plate_number} ({direction}) disimpan, "
            "menunggu pembayaran sebelum gate dibuka"
        )
>>>>>>> Stashed changes

    return VehicleCaptureOut(
        ignored=False,
        validated=True if direction == "keluar" else None,
        vehicle=VehicleOut(**to_out_dict(vehicle)),
<<<<<<< Updated upstream
        rfid_pending=True,
=======
        payment=PaymentInfo(**payment) if payment else None,
>>>>>>> Stashed changes
    )


async def handle_radar_event_masuk(request: Request) -> VehicleCaptureOut:
    """POST /api/hikvision/radar/masuk — terima event dari kamera ISAPI masuk."""
    return await handle_radar_event(request, forced_direction="masuk")


async def handle_radar_event_keluar(request: Request) -> VehicleCaptureOut:
    """POST /api/hikvision/radar/keluar — terima event dari kamera ISAPI keluar."""
    return await handle_radar_event(request, forced_direction="keluar")

