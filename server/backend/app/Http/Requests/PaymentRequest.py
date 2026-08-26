from pydantic import BaseModel, Field


class EntryPaymentRequest(BaseModel):
    plate_number: str = Field(min_length=1, max_length=20)
    entry_event_id: str = Field(min_length=1, max_length=36)


class EntryPaymentResponse(BaseModel):
    success: bool
    ticket_code: str
    order_id: str
    plate_number: str
    amount: int
    status: str
    snap_token: str | None = None
    redirect_url: str | None = None

class TicketPrintResponse(BaseModel):
    success: bool
    ticket_code: str
    barcode_value: str
    plate_number: str
    amount: int
    status: str
    entry_at: str | None = None
    paid_at: str | None = None


class TicketStatusResponse(BaseModel):
    success: bool
    ticket_code: str
    status: str
    can_print: bool
    can_open_gate: bool


class ExitTicketRequest(BaseModel):
    barcode_token: str = Field(min_length=1, max_length=128)
    exit_event_id: str | None = Field(default=None, max_length=36)


class ExitTicketResponse(BaseModel):
    success: bool
    valid: bool
    message: str
    ticket_code: str | None = None
    plate_number: str | None = None
    status: str | None = None