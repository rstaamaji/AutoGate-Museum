"""
Request/Response models — Server.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Direction = Literal["masuk", "keluar"]


class VehicleOut(BaseModel):
    id: int
    node_id: str
    direction: Direction
    plate_number: str
    plate_image_url: Optional[str] = None
    scene_image_url: Optional[str] = None
    confidence: Optional[float] = None
    captured_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleListOut(BaseModel):
    total: int
    items: list[VehicleOut]
