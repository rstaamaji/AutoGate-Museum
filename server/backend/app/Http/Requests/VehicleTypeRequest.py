"""
Request/Response models untuk VehicleType CRUD.
"""
from typing import Optional

from pydantic import BaseModel


class VehicleTypeCreateRequest(BaseModel):
    name: str


class VehicleTypeUpdateRequest(BaseModel):
    name: Optional[str] = None


class VehicleTypeOut(BaseModel):
    id: int
    name: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleTypeListOut(BaseModel):
    total: int
    items: list[VehicleTypeOut]
