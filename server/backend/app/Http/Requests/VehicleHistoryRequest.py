"""
Request/Response models untuk VehicleHistory dan VehicleEvent.
"""
from typing import Optional, Literal

from pydantic import BaseModel

Direction = Literal["masuk", "keluar"]


class VehicleEventOut(BaseModel):
    id: int
    event_id: str
    node_id: str
    plate_number: str
    direction: Direction
    plate_image_url: Optional[str] = None
    scene_image_url: Optional[str] = None
    confidence: Optional[float] = None
    captured_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleEventListOut(BaseModel):
    total: int
    items: list[VehicleEventOut]


class VehicleHistoryOut(BaseModel):
    id: int
    plate_number: str
    entry_event_id: Optional[str] = None
    exit_event_id: Optional[str] = None
    entry_node_id: Optional[str] = None
    exit_node_id: Optional[str] = None
    entry_node_name: Optional[str] = None
    exit_node_name: Optional[str] = None
    entry_at: Optional[str] = None
    exit_at: Optional[str] = None
    is_inside: bool = True
    owner_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleHistoryListOut(BaseModel):
    total: int
    items: list[VehicleHistoryOut]
