"""Request model untuk alur pembayaran kiosk di node."""
from pydantic import BaseModel, Field


class EntryPaymentRequest(BaseModel):
    plate_number: str = Field(min_length=1, max_length=20)
    entry_event_id: str = Field(min_length=1, max_length=36)


class ExitTicketRequest(BaseModel):
    barcode_token: str = Field(min_length=1, max_length=128)
    exit_event_id: str | None = Field(default=None, max_length=36)
