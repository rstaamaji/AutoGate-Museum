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
from app.Http.Controllers.HikvisionController import handle_radar_event
from app.Http.Requests.VehicleRequest import (
    Direction,
    VehicleCaptureOut,
    VehicleCaptureRequest,
    VehicleListOut,
)
from app.Http.Requests.RelayRequest import RelayControlRequest, RelayControlResponse
from app.Http.Middleware.auth import verify_api_key

router = APIRouter(prefix="/api")


# ── Kendaraan ──

@router.get("/plates", response_model=VehicleListOut)
def get_plates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    direction: Optional[Direction] = Query(None),
):
    """Ambil data kendaraan dari SQLite lokal."""
    return VehicleController.index(skip=skip, limit=limit, direction=direction)


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
    background_tasks: BackgroundTasks,
):
    """Terima event ISAPI dari kamera Hikvision (multipart/form-data + XML)."""
    return await handle_radar_event(request, background_tasks)


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
