"""
Request/Response models untuk Node CRUD.
"""
from typing import Optional

from pydantic import BaseModel


class NodeCreateRequest(BaseModel):
    name: str
    location: Optional[str] = None


class NodeUpdateRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class NodeOut(BaseModel):
    id: str
    name: str
    api_key: str
    location: Optional[str] = None
    status: str = "offline"
    last_seen_at: Optional[str] = None
    camera_in_active: bool = False
    camera_out_active: bool = False
    relay_in_active: bool = False
    relay_out_active: bool = False
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class NodeListOut(BaseModel):
    total: int
    items: list[NodeOut]
