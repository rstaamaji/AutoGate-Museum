"""
Controller kendaraan — Pos Satpam.
Trigger kamera, simpan ke SQLite, queue sync.

Flow baru: capture → simpan → tunggu RFID → buka pintu
"""
from typing import Optional

from fastapi import BackgroundTasks

from app.Http.Requests.VehicleRequest import (
    VehicleCaptureOut,
    VehicleCaptureRequest,
    VehicleListOut,
    VehicleOut,
)
from app.Services import VehicleService


def index(
    skip: int = 0,
    limit: int = 100,
    direction: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> VehicleListOut:
    """GET /api/plates — daftar kendaraan lokal."""
    items, total = VehicleService.get_all(
        skip=skip,
        limit=limit,
        direction=direction,
        search=search,
        start_date=start_date,
        end_date=end_date,
    )
    return VehicleListOut(
        total=total,
        items=[VehicleOut(**VehicleService.to_out_dict(v)) for v in items],
    )


def store(direction: str, payload: VehicleCaptureRequest, background_tasks: BackgroundTasks) -> VehicleCaptureOut:
    """
    POST /api/plates/{direction} — trigger kamera, simpan, tunggu RFID.

    Flow: capture → simpan → return rfid_pending → frontend tampilkan modal RFID.
    Gate dibuka setelah RFID diinput (atau dilewati) via POST /api/rfid.
    """
    outcome = VehicleService.capture_and_save(direction=direction, channel=payload.channel)

    return VehicleCaptureOut(
        ignored=outcome.ignored,
        reason=outcome.reason,
        validated=outcome.validated,
        vehicle=VehicleOut(**VehicleService.to_out_dict(outcome.vehicle)) if outcome.vehicle else None,
        rfid_pending=not outcome.ignored and outcome.vehicle is not None,
    )
