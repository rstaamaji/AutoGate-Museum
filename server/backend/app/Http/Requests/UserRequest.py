"""
Request/Response models untuk User CRUD.
"""
from typing import Optional, Literal

from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: Literal["super_admin", "admin", "pimpinan"]
    name: str


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Literal["super_admin", "admin", "pimpinan"]] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserListOut(BaseModel):
    total: int
    items: list[UserOut]
