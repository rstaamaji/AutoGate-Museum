import uuid
import hashlib

from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.Models.ParkingTicket import ParkingTicket
from app.Services.MidtransService import create_payment


def start_entry_payment(
    db: Session,
    plate_number: str,
    entry_event_id: str,
) -> dict:
    ticket = ParkingTicket(
        ticket_code=f"TKT-{uuid.uuid4().hex[:10].upper()}",
        barcode_token=uuid.uuid4().hex,
        plate_number=plate_number,
        entry_event_id=entry_event_id,
        amount=settings.TARIF_KARCIS,
        status="payment_pending",
        entry_at=datetime.now(timezone.utc),
    )

    db.add(ticket)
    db.flush()

    order_id = f"PARKIR-{ticket.ticket_code}"

    payment = create_payment(
        order_id=order_id,
        amount=ticket.amount,
        ticket_code=ticket.ticket_code,
    )

    ticket.order_id = order_id
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "ticket_code": ticket.ticket_code,
        "order_id": order_id,
        "plate_number": ticket.plate_number,
        "amount": ticket.amount,
        "status": ticket.status,
        "snap_token": payment.get("token"),
        "redirect_url": payment.get("redirect_url"),
    }

def verify_midtrans_signature(notification: dict) -> bool:
    raw_signature = (
        notification.get("order_id", "")
        + notification.get("status_code", "")
        + notification.get("gross_amount", "")
        + settings.MIDTRANS_SERVER_KEY
    )

    expected_signature = hashlib.sha512(
        raw_signature.encode("utf-8")
    ).hexdigest()

    return expected_signature == notification.get("signature_key")


def handle_payment_notification(
    db: Session,
    notification: dict,
) -> dict:
    if not verify_midtrans_signature(notification):
        raise HTTPException(
            status_code=401,
            detail="Signature Midtrans tidak valid",
        )

    order_id = notification.get("order_id")
    transaction_status = notification.get("transaction_status")
    fraud_status = notification.get("fraud_status")

    ticket = (
        db.query(ParkingTicket)
        .filter(ParkingTicket.order_id == order_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Karcis untuk order_id tidak ditemukan",
        )

    payment_success = (
        transaction_status == "settlement"
        or (
            transaction_status == "capture"
            and fraud_status == "accept"
        )
    )

    if payment_success:
        # Idempotent: webhook yang sama tidak diproses ulang
        if ticket.status != "paid":
            ticket.status = "paid"
            ticket.paid_at = datetime.now(timezone.utc)
            db.commit()

        return {
            "success": True,
            "message": "Pembayaran berhasil",
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
        }

    if transaction_status in ("deny", "cancel", "expire", "failure"):
        ticket.status = "payment_failed"
        db.commit()

        return {
            "success": True,
            "message": "Pembayaran gagal",
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
        }

    # Contoh: pending
    return {
        "success": True,
        "message": "Pembayaran masih menunggu",
        "ticket_code": ticket.ticket_code,
        "status": ticket.status,
    }

def get_ticket_print_data(
    db: Session,
    ticket_code: str,
) -> dict:
    ticket = db.query(ParkingTicket).filter(
        ParkingTicket.ticket_code == ticket_code
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Karcis tidak ditemukan",
        )

    if ticket.status != "paid":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Karcis belum bisa dicetak. "
                f"Status saat ini: {ticket.status}"
            ),
        )

    return {
        "success": True,
        "ticket_code": ticket.ticket_code,
        "barcode_value": ticket.barcode_token,
        "plate_number": ticket.plate_number,
        "amount": ticket.amount,
        "status": ticket.status,
        "entry_at": (
            ticket.entry_at.isoformat()
            if ticket.entry_at
            else None
        ),
        "paid_at": (
            ticket.paid_at.isoformat()
            if ticket.paid_at
            else None
        ),
    }


def get_ticket_status(db: Session, ticket_code: str) -> dict:
    ticket = db.query(ParkingTicket).filter(
        ParkingTicket.ticket_code == ticket_code
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Karcis tidak ditemukan")

    return {
        "success": True,
        "ticket_code": ticket.ticket_code,
        "status": ticket.status,
        "can_print": ticket.status == "paid",
        "can_open_gate": ticket.status == "paid",
    }


def validate_exit_ticket(db: Session, barcode_token: str) -> dict:
    ticket = db.query(ParkingTicket).filter(
        ParkingTicket.barcode_token == barcode_token
    ).first()

    if not ticket:
        return {"success": True, "valid": False, "message": "Barcode tidak dikenal"}

    if ticket.status != "paid":
        return {
            "success": True,
            "valid": False,
            "message": "Karcis belum dibayar atau sudah digunakan",
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
        }

    return {
        "success": True,
        "valid": True,
        "message": "Karcis valid untuk keluar",
        "ticket_code": ticket.ticket_code,
        "plate_number": ticket.plate_number,
        "status": ticket.status,
    }


def complete_exit_ticket(
    db: Session,
    barcode_token: str,
    exit_event_id: str | None = None,
) -> dict:
    ticket = db.query(ParkingTicket).filter(
        ParkingTicket.barcode_token == barcode_token
    ).with_for_update().first()

    if not ticket or ticket.status != "paid":
        return {
            "success": True,
            "valid": False,
            "message": "Karcis tidak valid atau sudah digunakan",
        }

    now = datetime.now(timezone.utc)
    ticket.status = "used"
    ticket.exit_event_id = exit_event_id
    ticket.exit_at = now
    ticket.used_at = now
    db.commit()

    return {
        "success": True,
        "valid": True,
        "message": "Karcis diterima dan ditandai sudah digunakan",
        "ticket_code": ticket.ticket_code,
        "plate_number": ticket.plate_number,
        "status": ticket.status,
    }