"""
Service komunikasi dengan kamera ANPR Hikvision.
Diadaptasi dari server/backend — untuk Pos Satpam.
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, TypedDict

import requests
import urllib3
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests_toolbelt.multipart import decoder

from app.config import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIRECTIONS = ("masuk", "keluar")

_PLATE_PIC_NAMES = ("licenseplatepicture", "plateimage", "platepicture", "licenseplate")
_SCENE_PIC_NAMES = ("detectionpicture", "sceneimage", "scenepicture", "vehicleimage", "detection")


class CameraResult(TypedDict):
    direction: str
    plate: Optional[str]
    is_known: bool
    confidence: Optional[float]
    captured_at: Optional[datetime]
    plate_image_bytes: Optional[bytes]
    scene_image_bytes: Optional[bytes]


class CameraError(Exception):
    """Kamera tidak bisa dihubungi / auth gagal / response aneh."""


class CameraConfig(TypedDict):
    host: str
    user: str
    password: str
    channel: int
    use_https: bool


def get_camera_config(direction: str) -> CameraConfig:
    direction = (direction or "").strip().lower()
    if direction == "masuk":
        return {
            "host": settings.CAMERA_IN_HOST,
            "user": settings.CAMERA_IN_USER,
            "password": settings.CAMERA_IN_PASSWORD,
            "channel": settings.CAMERA_IN_CHANNEL,
            "use_https": settings.CAMERA_IN_USE_HTTPS,
        }
    if direction == "keluar":
        return {
            "host": settings.CAMERA_OUT_HOST,
            "user": settings.CAMERA_OUT_USER,
            "password": settings.CAMERA_OUT_PASSWORD,
            "channel": settings.CAMERA_OUT_CHANNEL,
            "use_https": settings.CAMERA_OUT_USE_HTTPS,
        }
    raise CameraError(f"Arah kamera tidak dikenal: '{direction}'. Gunakan {DIRECTIONS}.")


def _get_auth_for(user: str, password: str, auth_type: str):
    if auth_type.lower() == "basic":
        return HTTPBasicAuth(user, password)
    return HTTPDigestAuth(user, password)


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
        try:
            captured_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            captured_at = None

    return {
        "plate": plate_elem.text.strip() if plate_elem is not None and plate_elem.text else None,
        "confidence": confidence,
        "captured_at": captured_at,
    }


def _is_unknown_plate(plate: Optional[str]) -> bool:
    if not plate or not plate.strip():
        return True
    return plate.strip().lower() in settings.UNKNOWN_PLATE_VALUES


def _pick_image(parts: dict, candidate_names: tuple, exclude_keys: set) -> Optional[bytes]:
    for key, content in parts.items():
        if key in exclude_keys:
            continue
        key_lower = key.lower()
        if any(cand in key_lower for cand in candidate_names):
            return content
    return None


def _split_plate_and_scene_images(parts: dict, xml_key: str) -> tuple:
    exclude = {xml_key}
    plate_image = _pick_image(parts, _PLATE_PIC_NAMES, exclude)
    scene_image = _pick_image(parts, _SCENE_PIC_NAMES, exclude)

    if plate_image is not None:
        exclude = exclude | {k for k, v in parts.items() if v is plate_image}
    if scene_image is not None:
        exclude = exclude | {k for k, v in parts.items() if v is scene_image}

    if plate_image is None or scene_image is None:
        remaining = [v for k, v in parts.items() if k not in exclude]
        for content in remaining:
            if plate_image is None:
                plate_image = content
            elif scene_image is None:
                scene_image = content

    return plate_image, scene_image


def check_camera_alive(direction: str) -> bool:
    """Cek apakah kamera bisa dihubungi. Return True jika hidup."""
    try:
        cam = get_camera_config(direction)
        scheme = "https" if cam["use_https"] else "http"
        url = f"{scheme}://{cam['host']}/ISAPI/System/deviceInfo"
        session = requests.Session()
        session.auth = _get_auth_for(cam["user"], cam["password"], settings.CAMERA_AUTH_TYPE)
        session.verify = False
        resp = session.get(url, timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def capture_plate(direction: str, channel: Optional[int] = None) -> CameraResult:
    """Ambil hasil ANPR terakhir dari kamera sesuai arah."""
    cam = get_camera_config(direction)
    scheme = "https" if cam["use_https"] else "http"
    ch = channel if channel is not None else cam["channel"]
    url = f"{scheme}://{cam['host']}/ISAPI/Traffic/MNPR/channels/{ch}"

    session = requests.Session()
    session.auth = _get_auth_for(cam["user"], cam["password"], settings.CAMERA_AUTH_TYPE)
    session.verify = False

    try:
        resp = session.get(url, timeout=settings.CAMERA_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise CameraError(f"Gagal menghubungi kamera '{direction}' di {url}: {e}") from e

    parts = _parse_mnpr_multipart(resp)

    xml_key = "mnpr.xml" if "mnpr.xml" in parts else next(
        (k for k in parts if k.lower().endswith(".xml") or "xml" in k.lower()), None
    )
    xml_bytes = parts.get(xml_key) if xml_key else None
    if not xml_bytes:
        raise CameraError(f"Response kamera '{direction}' tidak berisi metadata XML.")

    info = _extract_plate_from_xml(xml_bytes)
    plate_image_bytes, scene_image_bytes = _split_plate_and_scene_images(parts, xml_key)

    plate = info["plate"]
    is_known = not _is_unknown_plate(plate)

    return {
        "direction": direction,
        "plate": plate if is_known else None,
        "is_known": is_known,
        "confidence": info["confidence"],
        "captured_at": info["captured_at"],
        "plate_image_bytes": plate_image_bytes,
        "scene_image_bytes": scene_image_bytes,
    }
