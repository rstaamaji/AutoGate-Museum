"""
Mirip routes/api.php di Laravel — daftar semua endpoint.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.Http.Controllers import VehicleController
from app.Http.Requests.VehicleRequest import (
    Direction,
    VehicleCaptureOut,
    VehicleCaptureRequest,
    VehicleListOut,
)
from app.Http.Controllers.RelayController import RelayController
from app.Http.Requests.RelayRequest import RelayControlRequest, RelayControlResponse

# Kalau mau proteksi API key, tambahkan dependencies=[Depends(verify_api_key)]
# from app.Http.Middleware.auth import verify_api_key

router = APIRouter(prefix="/api", tags=["plates"])


@router.get("/plates", response_model=VehicleListOut)
def get_plates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    direction: Optional[Direction] = Query(None, description="Filter: masuk atau keluar"),
    db: Session = Depends(get_db),
):
    """Ambil semua data plat kendaraan yang tersimpan (opsional filter per arah)."""
    return VehicleController.index(db, skip=skip, limit=limit, direction=direction)


@router.post("/plates/{direction}", response_model=VehicleCaptureOut, status_code=201)
def create_plate(
    direction: Direction,
    background_tasks: BackgroundTasks,
    payload: VehicleCaptureRequest = VehicleCaptureRequest(),
    db: Session = Depends(get_db),
):
    """
    Trigger kamera ANPR arah tertentu ('masuk' atau 'keluar') untuk membaca
    plat + foto plat + foto scene terbaru, lalu simpan ke database.
    Kalau plat tidak terbaca (unknown), request diabaikan (ignored=true, tidak disimpan).
    """
    return VehicleController.store(db, direction, payload, background_tasks)


@router.post("/relay/control", response_model=RelayControlResponse)
def control_relay(payload: RelayControlRequest):
    """
    Endpoint untuk kontrol modbus relay.
    Menerima JSON dengan channel (int) dan status (bool).
    """
    return RelayController.control(payload)
