"""
Request/Response models untuk autentikasi.
"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# Resolve forward reference
LoginResponse.model_rebuild()
