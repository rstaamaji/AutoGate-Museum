"""
Request/Response models untuk VehicleOwner CRUD.
"""
from typing import Optional

from pydantic import BaseModel


class VehicleOwnerCreateRequest(BaseModel):
    plate_number: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    owner_phone: Optional[str] = None
    notes: Optional[str] = None


class VehicleOwnerUpdateRequest(BaseModel):
    plate_number: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    owner_phone: Optional[str] = None
    notes: Optional[str] = None


class VehicleOwnerOut(BaseModel):
    id: int
    plate_number: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    owner_phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleOwnerListOut(BaseModel):
    total: int
    items: list[VehicleOwnerOut]
