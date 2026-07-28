"""
Request/Response models untuk endpoint kendaraan — Pos Satpam.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Direction = Literal["masuk", "keluar"]


class VehicleCaptureRequest(BaseModel):
    """Body opsional untuk POST /api/plates/{direction}."""
    channel: Optional[int] = Field(
        default=None, description="Override channel ANPR kamera"
    )


class VehicleOut(BaseModel):
    id: int
    event_id: str
    direction: Direction
    plate_number: str
    plate_image_url: Optional[str] = None
    scene_image_url: Optional[str] = None
    confidence: Optional[float] = None
    captured_at: Optional[str] = None
    created_at: Optional[str] = None
    synced: bool = False


class VehicleListOut(BaseModel):
    total: int
    items: list[VehicleOut]


class VehicleCaptureOut(BaseModel):
    """Response POST /api/plates/{direction}."""
    ignored: bool
    reason: Optional[str] = None
    validated: Optional[bool] = None  # True=valid, False=ditolak, None=tidak perlu validasi (masuk)
    vehicle: Optional[VehicleOut] = None
