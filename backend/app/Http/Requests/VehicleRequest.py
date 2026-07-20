"""
Mirip app/Http/Requests/VehicleRequest.php di Laravel — validasi input & bentuk output.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Direction = Literal["masuk", "keluar"]


class VehicleCaptureRequest(BaseModel):
    """Body opsional untuk POST /api/plates/{direction}.
    Kosongkan untuk pakai konfigurasi kamera default (.env) sesuai arahnya."""

    channel: Optional[int] = Field(
        default=None, description="Override channel ANPR kamera, default ambil dari .env"
    )


class VehicleOut(BaseModel):
    id: int
    direction: Direction
    plate_number: str
    plate_image_url: Optional[str] = None
    scene_image_url: Optional[str] = None
    confidence: Optional[float] = None
    captured_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # pydantic v2, ganti dari orm_mode


class VehicleListOut(BaseModel):
    total: int
    items: list[VehicleOut]


class VehicleCaptureOut(BaseModel):
    """Response POST /api/plates/{direction}.
    Kalau plat tidak terbaca (unknown), ignored=True dan vehicle=None."""

    ignored: bool
    reason: Optional[str] = None
    vehicle: Optional[VehicleOut] = None
