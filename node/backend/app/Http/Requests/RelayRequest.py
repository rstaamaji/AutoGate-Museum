"""
Request/Response models untuk endpoint relay — Pos Satpam.
"""
from pydantic import BaseModel, Field


class RelayControlRequest(BaseModel):
    channel: int = Field(..., description="Channel relay (1, 2, 3, ...)")
    status: bool = Field(..., description="True = ON, False = OFF")


class RelayControlResponse(BaseModel):
    success: bool
    message: str
    channel: int
    status: bool
