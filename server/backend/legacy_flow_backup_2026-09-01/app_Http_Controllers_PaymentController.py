import uuid
import hashlib

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.Models.ParkingTicket import ParkingTicket
from app.Services.MidtransService import create_payment


def is_pending_ticket_expired(ticket: ParkingTicket) -> bool:
    if ticket.status != "pending":
        return False

    if not ticket.created_at:
        return False

    expired_at = ticket.created_at + timedelta(hours=settings.TICKET_PENDING_TTL_HOURS)
    return datetime.now(timezone.utc) > expired_at


def pending_ticket_expiry_hours(ticket: ParkingTicket) -> int:
    if not ticket.created_at:
        return settings.TICKET_PENDING_TTL_HOURS

    remaining = (
        ticket.created_at
        + timedelta(hours=settings.TICKET_PENDING_TTL_HOURS)
        - datetime.now(timezone.utc)
    ).total_seconds() / 3600
    return max(1, int(remaining))


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
        status="pending",
        entry_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    db.add(ticket)
    db.flush()

    order_id = f"PARKIR-{ticket.ticket_code}"

    payment = create_payment(
        order_id=order_id,
        amount=ticket.amount,
        ticket_code=ticket.ticket_code,
        expiry_hours=settings.TICKET_PENDING_TTL_HOURS,
    )

    ticket.order_id = order_id
    db.commit()
    db.refresh(ticket)

    payment_url = payment.get("redirect_url")
    if not payment_url:
        raise HTTPException(
            status_code=502,
            detail="Midtrans tidak mengembalikan redirect URL pembayaran",
        )

    # Cetak karcis secara fisik (tanpa memblokir response jika terjadi error)
    cetak_karcis_fisik(
        ticket_code=ticket.ticket_code,
        barcode_token=ticket.barcode_token,
        redirect_url=payment_url,
        plate_number=ticket.plate_number
    )

    return {
        "success": True,
        "ticket_code": ticket.ticket_code,
        "order_id": order_id,
        "plate_number": ticket.plate_number,
        "amount": ticket.amount,
        "status": ticket.status,
        "barcode_token": ticket.barcode_token,
        "snap_token": payment.get("token"),
        "redirect_url": payment_url,
    }


def create_ticket_payment(db: Session, barcode_token: str) -> dict:
    ticket = db.query(ParkingTicket).filter(
        ParkingTicket.barcode_token == barcode_token
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Karcis tidak ditemukan")
    if ticket.status != "pending":
        raise HTTPException(status_code=409, detail="Karcis tidak sedang menunggu pembayaran")
    if is_pending_ticket_expired(ticket):
        raise HTTPException(status_code=410, detail="Karcis pending sudah kedaluwarsa")

    if ticket.payment_redirect_url:
        return {
            "success": True,
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
            "redirect_url": ticket.payment_redirect_url,
        }

    payment = create_payment(
        order_id=ticket.order_id or f"PARKIR-{ticket.ticket_code}",
        amount=ticket.amount,
        ticket_code=ticket.ticket_code,
        expiry_hours=pending_ticket_expiry_hours(ticket),
    )
    ticket.order_id = ticket.order_id or f"PARKIR-{ticket.ticket_code}"
    ticket.payment_token = payment.get("token")
    ticket.payment_redirect_url = payment.get("redirect_url")
    ticket.payment_created_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "ticket_code": ticket.ticket_code,
        "status": ticket.status,
        "redirect_url": ticket.payment_redirect_url,
        "snap_token": ticket.payment_token,
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
        # Status tiket tetap mengikuti status utama: pending -> paid -> used.
        # Penolakan atau expire tidak menurunkan status tiket ke status baru yang tidak terdefinisi.
        db.commit()

        return {
            "success": True,
            "message": "Pembayaran gagal atau kedaluwarsa",
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
        }

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

    if ticket.status not in {"pending", "paid"}:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Karcis tidak valid untuk dicetak. "
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

    if ticket.status == "pending":
        if is_pending_ticket_expired(ticket):
            return {
                "success": True,
                "valid": False,
                "message": "Karcis pending sudah kedaluwarsa",
                "ticket_code": ticket.ticket_code,
                "status": ticket.status,
            }
        return {
            "success": True,
            "valid": False,
            "message": "Karcis belum dibayar",
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
        }

    if ticket.status == "used":
        return {
            "success": True,
            "valid": False,
            "message": "Karcis sudah digunakan",
            "ticket_code": ticket.ticket_code,
            "status": ticket.status,
        }

    if ticket.status != "paid":
        return {
            "success": True,
            "valid": False,
            "message": "Karcis tidak valid untuk keluar",
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


def cetak_karcis_fisik(ticket_code: str, barcode_token: str, redirect_url: str, plate_number: str):
    """
    Memanggil print_ticket.py sebagai proses Windows terpisah (non-blocking).
    Ini diperlukan karena Windows Print Spooler (Win32Raw) harus berjalan
    dari proses utama Windows, bukan dari dalam worker thread FastAPI.
    """
    import subprocess
    import sys
    import os

    script_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "print_ticket.py")
    script_path = os.path.abspath(script_path)

    try:
        proc = subprocess.Popen(
            [sys.executable, script_path, ticket_code, barcode_token, redirect_url, plate_number],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # Jalankan di direktori backend agar .env terbaca
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
        )
        print(f"[PRINTER] Proses cetak dimulai (PID: {proc.pid})")
    except Exception as e:
        print(f"[PRINTER ERROR] Gagal memulai proses cetak: {e}")