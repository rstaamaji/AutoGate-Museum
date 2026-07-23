"""
Controller kendaraan — Pos Satpam.
Trigger kamera, simpan ke SQLite, queue sync.
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
from app.Http.Controllers.RelayController import RelayController


def index(skip: int = 0, limit: int = 100, direction: Optional[str] = None) -> VehicleListOut:
    """GET /api/plates — daftar kendaraan lokal."""
    items, total = VehicleService.get_all(skip=skip, limit=limit, direction=direction)
    return VehicleListOut(
        total=total,
        items=[VehicleOut(**VehicleService.to_out_dict(v)) for v in items],
    )


def store(direction: str, payload: VehicleCaptureRequest, background_tasks: BackgroundTasks) -> VehicleCaptureOut:
    """POST /api/plates/{direction} — trigger kamera, simpan, buka gate."""
    outcome = VehicleService.capture_and_save(direction=direction, channel=payload.channel)

    # Jika plat terbaca, otomatis buka gate
    if not outcome.ignored and outcome.vehicle:
        relay_channel = 1 if direction == "masuk" else 2
        background_tasks.add_task(RelayController.open_and_close_delayed, relay_channel, 15)

    return VehicleCaptureOut(
        ignored=outcome.ignored,
        reason=outcome.reason,
        vehicle=VehicleOut(**VehicleService.to_out_dict(outcome.vehicle)) if outcome.vehicle else None,
    )
