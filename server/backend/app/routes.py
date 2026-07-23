"""
Routes API — Server.
Hanya monitoring + terima data dari node.
Tidak ada endpoint kontrol relay/stream.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.Http.Controllers import VehicleController
from app.Http.Controllers.SyncController import receive_vehicle_data
from app.Http.Controllers.NodeController import (
    register_node,
    update_node_status,
    get_all_nodes,
    get_node,
)
from app.Http.Requests.VehicleRequest import Direction, VehicleListOut

router = APIRouter(prefix="/api")


# ── Kendaraan (read-only) ──

@router.get("/vehicles", response_model=VehicleListOut)
def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    direction: Optional[Direction] = Query(None),
    node_id: Optional[str] = Query(None, description="Filter per node"),
    db: Session = Depends(get_db),
):
    """Ambil data kendaraan dari semua node."""
    return VehicleController.index(db, skip=skip, limit=limit, direction=direction, node_id=node_id)


# ── Sinkronisasi (terima data dari node) ──

@router.post("/sync/vehicles", status_code=201)
def sync_vehicle(payload: dict, db: Session = Depends(get_db)):
    """Terima data kendaraan dari pos satpam (node)."""
    return receive_vehicle_data(db, payload)


# ── Node Management ──

@router.post("/nodes/register", status_code=201)
def register(payload: dict, db: Session = Depends(get_db)):
    """Registrasi pos satpam (node) baru."""
    return register_node(
        db,
        node_id=payload.get("node_id", ""),
        name=payload.get("name", ""),
        location=payload.get("location"),
    )


@router.put("/nodes/{node_id}/status")
def update_status(node_id: str, payload: dict, db: Session = Depends(get_db)):
    """Update status node via heartbeat dari pos satpam."""
    return update_node_status(db, node_id, payload)


@router.get("/nodes")
def list_nodes(db: Session = Depends(get_db)):
    """Ambil semua node + status perangkat."""
    return get_all_nodes(db)


@router.get("/nodes/{node_id}")
def get_node_detail(node_id: str, db: Session = Depends(get_db)):
    """Ambil detail satu node."""
    result = get_node(db, node_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Node tidak ditemukan")
    return result


# ── Dashboard Summary ──

@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Ringkasan untuk dashboard monitoring."""
    from app.Models.Vehicle import Vehicle
    from app.Models.Node import Node
    from datetime import datetime, timedelta

    total_vehicles = db.query(Vehicle).count()
    total_nodes = db.query(Node).count()
    online_nodes = db.query(Node).filter(Node.status == "online").count()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_vehicles = db.query(Vehicle).filter(Vehicle.created_at >= today_start).count()

    return {
        "total_vehicles": total_vehicles,
        "today_vehicles": today_vehicles,
        "total_nodes": total_nodes,
        "online_nodes": online_nodes,
        "offline_nodes": total_nodes - online_nodes,
    }
