"""
Service untuk mengambil snapshot dari kamera Hikvision.
Untuk Pos Satpam — langsung akses kamera lokal.
"""
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth

from app.config import settings
from app.Services.CameraService import get_camera_config, CameraError


def _get_auth_for(user: str, password: str, auth_type: str):
    if auth_type.lower() == "basic":
        return HTTPBasicAuth(user, password)
    return HTTPDigestAuth(user, password)


def get_snapshot(direction: str) -> bytes:
    """Ambil 1 frame JPEG terbaru dari kamera."""
    cam = get_camera_config(direction)
    scheme = "https" if cam["use_https"] else "http"
    url = f"{scheme}://{cam['host']}/ISAPI/Streaming/channels/{cam['channel']}/picture"

    session = requests.Session()
    session.auth = _get_auth_for(cam["user"], cam["password"], settings.CAMERA_AUTH_TYPE)
    session.verify = False

    try:
        resp = session.get(url, timeout=settings.CAMERA_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise CameraError(f"Gagal mengambil snapshot kamera '{direction}': {e}") from e

    return resp.content
