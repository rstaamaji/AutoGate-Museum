"""
Mirip app/Services/CameraService.php — logika bisnis untuk komunikasi dengan
kamera ANPR Hikvision, diadaptasi dari script hikvision_anpr_ondemand.py
(metode --method mnpr, yang terbukti jalan di DS-TCG406-E).

Kamera dipanggil ON-DEMAND: setiap kali endpoint POST /api/plates dipanggil,
kita GET hasil ANPR TERAKHIR yang sudah direkam kamera lewat ISAPI MNPR.
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, TypedDict

import requests
import urllib3
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests_toolbelt.multipart import decoder

from app.config import settings

# kamera Hikvision umumnya pakai self-signed cert kalau HTTPS -> matikan warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CameraResult(TypedDict):
    plate: Optional[str]
    confidence: Optional[float]
    captured_at: Optional[datetime]
    image_bytes: Optional[bytes]


class CameraError(Exception):
    """Dilempar kalau kamera tidak bisa dihubungi / auth gagal / response aneh."""


def _get_auth(auth_type: str):
    if auth_type.lower() == "basic":
        return HTTPBasicAuth(settings.CAMERA_USER, settings.CAMERA_PASSWORD)
    return HTTPDigestAuth(settings.CAMERA_USER, settings.CAMERA_PASSWORD)


def _strip_ns(root: ET.Element):
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]
    return root


def _parse_mnpr_multipart(resp: requests.Response) -> dict:
    content_type = resp.headers.get("Content-Type", "")
    if "multipart" not in content_type:
        raise CameraError(f"Content-Type tidak dikenali dari kamera: {content_type}")

    multipart_data = decoder.MultipartDecoder.from_response(resp)
    parts: dict[str, bytes] = {}

    for part in multipart_data.parts:
        disposition = part.headers.get(b"Content-Disposition", b"").decode(errors="ignore")
        name = None
        for chunk in disposition.split(";"):
            chunk = chunk.strip()
            if chunk.startswith("name="):
                name = chunk.split("=", 1)[1].strip('"')
                break
        parts[name or f"part_{len(parts)}"] = part.content

    return parts


def _extract_plate_from_xml(xml_bytes: bytes) -> dict:
    root = ET.fromstring(xml_bytes)
    _strip_ns(root)

    plate_elem = root.find(".//licensePlate")
    conf_elem = root.find(".//confidenceLevel")
    time_elem = root.find(".//dateTime")

    confidence = None
    if conf_elem is not None and conf_elem.text:
        try:
            confidence = float(conf_elem.text.strip())
        except ValueError:
            confidence = None

    captured_at = None
    if time_elem is not None and time_elem.text:
        raw = time_elem.text.strip()
        # format Hikvision biasanya ISO8601, contoh: 2024-05-01T10:20:30+07:00
        try:
            captured_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            captured_at = None

    return {
        "plate": plate_elem.text.strip() if plate_elem is not None and plate_elem.text else None,
        "confidence": confidence,
        "captured_at": captured_at,
    }


def capture_plate(channel: Optional[int] = None) -> CameraResult:
    """
    Ambil hasil ANPR terakhir dari kamera via GET /ISAPI/Traffic/MNPR/channels/<channel>.
    Melempar CameraError kalau kamera tidak bisa dihubungi.
    """
    scheme = "https" if settings.CAMERA_USE_HTTPS else "http"
    ch = channel if channel is not None else settings.CAMERA_CHANNEL
    url = f"{scheme}://{settings.CAMERA_HOST}/ISAPI/Traffic/MNPR/channels/{ch}"

    session = requests.Session()
    session.auth = _get_auth(settings.CAMERA_AUTH_TYPE)
    session.verify = False

    try:
        resp = session.get(url, timeout=settings.CAMERA_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise CameraError(f"Gagal menghubungi kamera di {url}: {e}") from e

    parts = _parse_mnpr_multipart(resp)

    xml_bytes = parts.get("mnpr.xml")
    if not xml_bytes:
        raise CameraError("Response kamera tidak berisi metadata XML (mnpr.xml).")

    info = _extract_plate_from_xml(xml_bytes)

    image_bytes = None
    for name, content in parts.items():
        if name != "mnpr.xml":
            image_bytes = content  # ambil gambar pertama yang ditemukan
            break

    return {
        "plate": info["plate"],
        "confidence": info["confidence"],
        "captured_at": info["captured_at"],
        "image_bytes": image_bytes,
    }
