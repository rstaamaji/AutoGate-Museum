from pydantic import BaseModel, Field

class RelayControlRequest(BaseModel):
    channel: int = Field(..., description="Channel relay (contoh: 1, 2, 3)")
    status: bool = Field(..., description="Status relay (True = ON, False = OFF)")

class RelayControlResponse(BaseModel):
    success: bool
    message: str
    channel: int
    status: bool
