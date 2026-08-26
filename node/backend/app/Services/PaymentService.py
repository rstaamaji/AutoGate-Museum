"""
Komunikasi pembayaran node -> server.
Node tidak menyimpan server key Midtrans; node hanya meneruskan request kiosk.
"""
import httpx
from fastapi import HTTPException, status

from app.config import settings


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if settings.SERVER_API_KEY:
        headers["X-API-Key"] = settings.SERVER_API_KEY
    return headers


def start_entry_payment(plate_number: str, entry_event_id: str) -> dict:
    try:
        response = httpx.post(
            f"{settings.SERVER_URL}/api/tickets/entry-payment",
            json={
                "plate_number": plate_number,
                "entry_event_id": entry_event_id,
            },
            headers=_headers(),
            timeout=30,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Server pembayaran tidak dapat dihubungi: {exc}",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


def get_ticket_status(ticket_code: str) -> dict:
    try:
        response = httpx.get(
            f"{settings.SERVER_URL}/api/tickets/{ticket_code}/status",
            headers=_headers(),
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Server pembayaran tidak dapat dihubungi: {exc}",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


def get_ticket_print_data(ticket_code: str) -> dict:
    try:
        response = httpx.get(
            f"{settings.SERVER_URL}/api/tickets/{ticket_code}/print-data",
            headers=_headers(),
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Data karcis tidak dapat diambil: {exc}",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


def validate_exit(barcode_token: str) -> dict:
    return _post_exit("validate-exit", barcode_token)


def complete_exit(barcode_token: str, exit_event_id: str | None = None) -> dict:
    return _post_exit("complete-exit", barcode_token, exit_event_id)


def _post_exit(
    action: str,
    barcode_token: str,
    exit_event_id: str | None = None,
) -> dict:
    payload = {"barcode_token": barcode_token}
    if exit_event_id:
        payload["exit_event_id"] = exit_event_id

    try:
        response = httpx.post(
            f"{settings.SERVER_URL}/api/tickets/{action}",
            json=payload,
            headers=_headers(),
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Validasi karcis tidak dapat dilakukan: {exc}",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()
