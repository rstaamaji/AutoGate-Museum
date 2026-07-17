"""
Mirip routes/api.php di Laravel — daftar semua endpoint.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.Http.Controllers import VehicleController
from app.Http.Requests.VehicleRequest import VehicleCaptureRequest, VehicleListOut, VehicleOut

# Kalau mau proteksi API key, tambahkan dependencies=[Depends(verify_api_key)]
# from app.Http.Middleware.auth import verify_api_key

router = APIRouter(prefix="/api", tags=["plates"])


@router.get("/plates", response_model=VehicleListOut)
def get_plates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Ambil semua data plat kendaraan yang tersimpan."""
    return VehicleController.index(db, skip=skip, limit=limit)


@router.post("/plates", response_model=VehicleOut, status_code=201)
def create_plate(
    payload: VehicleCaptureRequest = VehicleCaptureRequest(),
    db: Session = Depends(get_db),
):
    """Trigger kamera ANPR untuk membaca plat & gambar terbaru, lalu simpan ke database."""
    return VehicleController.store(db, payload)
