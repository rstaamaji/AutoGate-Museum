"""
Controller stream/snapshot kamera — Pos Satpam.
"""
import logging

from fastapi import HTTPException
from fastapi.responses import Response

from app.Services import StreamService
from app.Services.CameraService import CameraError

logger = logging.getLogger(__name__)


def live(direction: str):
    """GET /api/stream/{direction} — 1 frame JPEG terkini."""
    try:
        image_bytes = StreamService.get_snapshot(direction)
        return Response(content=image_bytes, media_type="image/jpeg")
    except CameraError as e:
        logger.error(f"Stream error {direction}: {e}")
        raise HTTPException(status_code=502, detail=str(e))
