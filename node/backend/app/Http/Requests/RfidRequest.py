"""
Request/Response models untuk endpoint RFID — Pos Satpam.
"""
from typing import Optional

from pydantic import BaseModel


class RfidRequest(BaseModel):
    """Body untuk POST /api/rfid."""
    event_id: str
    rfid_uid: Optional[str] = None  # null/empty = "Lanjutkan" tanpa RFID


class RfidResponse(BaseModel):
    """Response POST /api/rfid."""
    success: bool
    message: str
    rfid_match: Optional[bool] = None  # True=cocok, False=beda, None=N/A
