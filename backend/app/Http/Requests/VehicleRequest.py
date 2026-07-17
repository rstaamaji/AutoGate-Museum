"""
Mirip app/Http/Requests/VehicleRequest.php di Laravel — validasi input & bentuk output.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VehicleCaptureRequest(BaseModel):
    """Body opsional untuk POST /api/plates.
    Kosongkan semua field untuk pakai konfigurasi default (.env)."""

    channel: Optional[int] = Field(
        default=None, description="Override channel ANPR kamera, default ambil dari .env"
    )


class VehicleOut(BaseModel):
    id: int
    plate_number: str
    image_url: str
    confidence: Optional[float] = None
    captured_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # pydantic v2, ganti dari orm_mode


class VehicleListOut(BaseModel):
    total: int
    items: list[VehicleOut]
