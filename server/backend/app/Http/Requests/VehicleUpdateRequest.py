"""
Request model untuk update kendaraan (tipe & cc).
"""
from typing import Optional

from pydantic import BaseModel, Field


class VehicleUpdateRequest(BaseModel):
    vehicle_type: Optional[str] = None
    cc: Optional[int] = Field(None, ge=0, le=9999)
