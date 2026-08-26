"""
Routes API — Pos Satpam.
"""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, HTTPException, Request
from fastapi.responses import Response

from app.Http.Controllers import VehicleController, StreamController
from app.Http.Controllers.RelayController import RelayController
from app.Http.Controllers.StatusController import get_status
from app.Http.Controllers.SyncController import get_sync_status, manual_sync
from app.Http.Controllers.SettingsController import get_settings, update_settings
from app.Http.Controllers.HikvisionController import (
    handle_radar_event,
    handle_radar_event_masuk,
    handle_radar_event_keluar,
)
from app.Http.Controllers.RfidController import handle_rfid
from app.Http.Requests.VehicleRequest import (
    Direction,
    VehicleCaptureOut,
    VehicleCaptureRequest,
    VehicleListOut,
)
from app.Http.Requests.RelayRequest import RelayControlRequest, RelayControlResponse
<<<<<<< Updated upstream
from app.Http.Requests.RfidRequest import RfidRequest, RfidResponse
=======
from app.Http.Requests.PaymentRequest import EntryPaymentRequest, ExitTicketRequest
>>>>>>> Stashed changes
from app.Http.Middleware.auth import verify_api_key
from app.Services import PaymentService

router = APIRouter(prefix="/api")


# ── Kendaraan ──

@router.get("/plates", response_model=VehicleListOut)
def get_plates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    direction: Optional[Direction] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """Ambil data kendaraan dari SQLite lokal."""
    return VehicleController.index(
        skip=skip,
        limit=limit,
        direction=direction,
        search=search,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/plates/{direction}", response_model=VehicleCaptureOut, status_code=201)
def create_plate(
    direction: Direction,
    background_tasks: BackgroundTasks,
    payload: VehicleCaptureRequest = VehicleCaptureRequest(),
):
    """Trigger kamera, simpan ke SQLite, queue sync, buka gate."""
    return VehicleController.store(direction, payload, background_tasks)


@router.post("/hikvision/radar", response_model=VehicleCaptureOut, status_code=201)
async def hikvision_radar(
    request: Request,
):
    """Terima event ISAPI dari kamera Hikvision (auto-detect IP)."""
    return await handle_radar_event(request)


@router.post("/hikvision/radar/masuk", response_model=VehicleCaptureOut, status_code=201)
async def hikvision_radar_masuk(
    request: Request,
):
    """Terima event ISAPI dari kamera Hikvision Masuk."""
    return await handle_radar_event_masuk(request)


@router.post("/hikvision/radar/keluar", response_model=VehicleCaptureOut, status_code=201)
async def hikvision_radar_keluar(
    request: Request,
):
    """Terima event ISAPI dari kamera Hikvision Keluar."""
    return await handle_radar_event_keluar(request)



# ── RFID ──

@router.post("/rfid", response_model=RfidResponse)
def submit_rfid(payload: RfidRequest, background_tasks: BackgroundTasks):
    """Input RFID setelah ANPR capture — update data + buka gate."""
    return handle_rfid(payload.event_id, payload.rfid_uid, background_tasks)


@router.post("/payment/start")
def start_payment(
    payload: EntryPaymentRequest,
    _: None = Depends(verify_api_key),
):
    """Kiosk meminta server membuat pembayaran karcis masuk."""
    return PaymentService.start_entry_payment(
        plate_number=payload.plate_number,
        entry_event_id=payload.entry_event_id,
    )


@router.get("/payment/status/{ticket_code}")
def payment_status(
    ticket_code: str,
    _: None = Depends(verify_api_key),
):
    """Kiosk memantau status pembayaran karcis."""
    return PaymentService.get_ticket_status(ticket_code)


@router.get("/payment/print-data/{ticket_code}")
def payment_print_data(
    ticket_code: str,
    _: None = Depends(verify_api_key),
):
    """Ambil barcode karcis yang sudah lunas untuk printer kiosk."""
    return PaymentService.get_ticket_print_data(ticket_code)


@router.post("/payment/complete-entry/{ticket_code}")
async def complete_entry_payment(
    ticket_code: str,
    _: None = Depends(verify_api_key),
):
    """Buka gate masuk hanya setelah server menyatakan karcis paid."""
    payment_status = PaymentService.get_ticket_status(ticket_code)
    if not payment_status.get("can_open_gate"):
        raise HTTPException(
            status_code=409,
            detail="Pembayaran belum berhasil; gate tetap tertutup.",
        )

    print_data = PaymentService.get_ticket_print_data(ticket_code)
    await RelayController.open_and_close_delayed(1, 15)
    return {"success": True, "ticket": print_data, "gate_opened": True}


@router.post("/payment/validate-exit")
def validate_exit_payment(
    payload: ExitTicketRequest,
    _: None = Depends(verify_api_key),
):
    """Scanner meminta validasi barcode sebelum gate keluar dibuka."""
    return PaymentService.validate_exit(payload.barcode_token)


@router.post("/payment/complete-exit")
async def complete_exit_payment(
    payload: ExitTicketRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_api_key),
):
    """Tandai karcis digunakan lalu buka gate keluar."""
    result = PaymentService.complete_exit(
        payload.barcode_token,
        payload.exit_event_id,
    )
    if not result.get("valid"):
        raise HTTPException(status_code=409, detail=result.get("message"))

    background_tasks.add_task(
        RelayController.open_and_close_delayed,
        4,
        15,
    )
    return {"success": True, "ticket": result, "gate_opened": True}


# ── Relay/Gate ──

@router.post("/relay/control", response_model=RelayControlResponse)
def control_relay(payload: RelayControlRequest):
    """Kontrol modbus relay (buka/tutup gate)."""
    return RelayController.control(payload, triggered_by="manual")


# ── Stream ──

@router.get("/stream/{direction}")
def stream_live(direction: Direction):
    """1 frame JPEG terkini dari kamera."""
    return StreamController.live(direction)


# ── Status ──

@router.get("/status")
def device_status():
    """Status kamera & relay saat ini."""
    return get_status()


# ── Sinkronisasi ──

@router.get("/sync/status")
def sync_status():
    """Status sinkronisasi (pending, sent, failed, server online)."""
    return get_sync_status()


@router.post("/sync/manual")
async def trigger_manual_sync():
    """Trigger sinkronisasi manual ke server."""
    return await manual_sync()


# ── Settings ──

@router.get("/settings")
def read_settings():
    """Baca semua konfigurasi node."""
    return get_settings()


@router.put("/settings")
def write_settings(payload: dict):
    """Update konfigurasi node (.env file)."""
    try:
        return update_settings(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
