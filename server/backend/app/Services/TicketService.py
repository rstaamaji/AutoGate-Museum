import secrets
from datetime import datetime, timezone

from app.config import settings
from app.Models.ParkingTicket import ParkingTicket


def create_ticket(db, plate_number: str, entry_event_id: str):
    ticket_code = f"TKT-{secrets.token_hex(6).upper()}"
    barcode_token = secrets.token_urlsafe(32)

    ticket = ParkingTicket(
        ticket_code=ticket_code,
        barcode_token=barcode_token,
        plate_number=plate_number,
        entry_event_id=entry_event_id,
        amount=settings.TARIF_KARCIS,
        status="payment_pending",
        entry_at=datetime.now(timezone.utc),
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket