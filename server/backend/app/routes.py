"""
Routes API — Server v3.0.

Endpoint publik:
- POST /api/auth/login

Endpoint user (JWT):
- GET  /api/auth/me
- GET  /api/users (super_admin)
- POST /api/users (super_admin)
- PUT  /api/users/{id} (super_admin)
- DELETE /api/users/{id} (super_admin)
- GET  /api/nodes (admin, super_admin)
- POST /api/nodes (super_admin)
- GET  /api/nodes/{id} (admin, super_admin)
- PUT  /api/nodes/{id} (super_admin)
- DELETE /api/nodes/{id} (super_admin)
- CRUD /api/vehicle-owners (admin, super_admin)
- CRUD /api/vehicle-types (admin, super_admin)
- PUT  /api/vehicles/{id} (admin, super_admin)
- GET  /api/vehicles/events (all authenticated)
- GET  /api/vehicles/history (all authenticated)
- GET  /api/vehicles/history/{id} (all authenticated)
- GET  /api/dashboard/summary (all authenticated)

Endpoint node (API key):
- POST /api/sync/events
- GET  /api/sync/validate/{plate_number}
- PUT  /api/nodes/{node_id}/status
"""
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.Http.Middleware.auth import get_current_user, require_role, verify_node_api_key
from app.Http.Requests.AuthRequest import LoginRequest, LoginResponse, UserInfo
from app.Http.Requests.UserRequest import UserCreateRequest, UserUpdateRequest, UserOut, UserListOut
from app.Http.Requests.NodeRequest import NodeCreateRequest, NodeUpdateRequest, NodeOut, NodeListOut
from app.Http.Requests.VehicleOwnerRequest import (
    VehicleOwnerCreateRequest,
    VehicleOwnerUpdateRequest,
    VehicleOwnerOut,
    VehicleOwnerListOut,
)
from app.Http.Requests.VehicleTypeRequest import (
    VehicleTypeCreateRequest,
    VehicleTypeUpdateRequest,
    VehicleTypeOut,
    VehicleTypeListOut,
)
from app.Http.Requests.VehicleHistoryRequest import (
    VehicleEventListOut,
    VehicleHistoryOut,
    VehicleHistoryListOut,
)
from app.Http.Requests.VehicleUpdateRequest import VehicleUpdateRequest

from app.Http.Controllers.AuthController import login, get_me
from app.Http.Controllers.UserController import (
    list_users,
    create_user,
    update_user,
    delete_user,
)
from app.Http.Controllers.NodeController import (
    create_node,
    list_nodes,
    get_node,
    update_node,
    delete_node,
)
from app.Http.Controllers.VehicleOwnerController import (
    list_owners,
    create_owner,
    update_owner,
    delete_owner,
)
from app.Http.Controllers.VehicleController import search_vehicles, list_vehicles, update_vehicle
from app.Http.Controllers.VehicleTypeController import list_types, create_type, update_type, delete_type
from app.Http.Controllers.VehicleHistoryController import (
    list_events,
    list_history,
    get_history_detail,
)
from app.Http.Controllers.SyncController import receive_event, validate_plate
from app.Models.Node import Node

router = APIRouter(prefix="/api")


# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════

@router.post("/auth/login", response_model=LoginResponse)
def auth_login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login dengan username + password. Return JWT token."""
    return login(db, request)


@router.get("/auth/me", response_model=UserInfo)
def auth_me(current_user=Depends(get_current_user)):
    """Info user dari token."""
    return get_me(current_user)


# ══════════════════════════════════════════════════════════════
# USER MANAGEMENT (super_admin only)
# ══════════════════════════════════════════════════════════════

@router.get("/users", response_model=UserListOut)
def api_list_users(
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return list_users(db)


@router.post("/users", response_model=UserOut, status_code=201)
def api_create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return create_user(db, request)


@router.put("/users/{user_id}", response_model=UserOut)
def api_update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return update_user(db, user_id, request)


@router.delete("/users/{user_id}")
def api_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return delete_user(db, user_id)


# ══════════════════════════════════════════════════════════════
# NODE MANAGEMENT (admin, super_admin — write: super_admin only)
# ══════════════════════════════════════════════════════════════

@router.get("/nodes", response_model=NodeListOut)
def api_list_nodes(
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    return list_nodes(db)


@router.post("/nodes", response_model=NodeOut, status_code=201)
def api_create_node(
    request: NodeCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return create_node(db, request)


@router.get("/nodes/{node_id}", response_model=NodeOut)
def api_get_node(
    node_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    return get_node(db, node_id)


@router.put("/nodes/{node_id}", response_model=NodeOut)
def api_update_node(
    node_id: str,
    request: NodeUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return update_node(db, node_id, request)


@router.delete("/nodes/{node_id}")
def api_delete_node(
    node_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin")),
):
    return delete_node(db, node_id)


# ══════════════════════════════════════════════════════════════
# NODE → SERVER (node auth via API key)
# Status node ditentukan dari aktivitas sync (last_seen_at)
# ══════════════════════════════════════════════════════════════

@router.post("/nodes/ping")
def api_node_ping(
    db: Session = Depends(get_db),
    node: Node = Depends(verify_node_api_key),
):
    """Node ping server — update last_seen_at. Dipanggil periodik oleh SyncService."""
    from datetime import datetime, timezone
    node.last_seen_at = datetime.now(timezone.utc)
    node.status = "online"
    db.commit()
    return {"success": True, "node_id": node.id, "name": node.name}


@router.post("/sync/events", status_code=201)
def api_sync_event(
    payload: dict,
    db: Session = Depends(get_db),
    node: Node = Depends(verify_node_api_key),
):
    """Node push event masuk/keluar ke server. Otomatis update status node."""
    payload["node_id"] = node.id
    return receive_event(db, payload)


@router.get("/sync/validate/{plate_number}")
def api_validate_plate(
    plate_number: str,
    db: Session = Depends(get_db),
    node: Node = Depends(verify_node_api_key),
):
    """Node tanya: apakah plat ini sedang di dalam? Otomatis update status node."""
    return validate_plate(db, plate_number, node_id=node.id)


# ══════════════════════════════════════════════════════════════
# VEHICLES (admin, super_admin)
# ══════════════════════════════════════════════════════════════

@router.get("/vehicles")
def api_list_vehicles(
    q: str = Query("", description="Cari plat nomor"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    """List kendaraan + search (untuk dropdown dan halaman kendaraan)."""
    return list_vehicles(db, q=q, skip=skip, limit=limit)


@router.put("/vehicles/{vehicle_id}")
def api_update_vehicle(
    vehicle_id: int,
    request: VehicleUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    """Update tipe kendaraan dan/atau cc kendaraan."""
    return update_vehicle(db, vehicle_id, request)


# ══════════════════════════════════════════════════════════════
# VEHICLE TYPE (admin, super_admin)
# ══════════════════════════════════════════════════════════════

@router.get("/vehicle-types", response_model=VehicleTypeListOut)
def api_list_types(
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    """Daftar semua tipe kendaraan."""
    return list_types(db)


@router.post("/vehicle-types", response_model=VehicleTypeOut, status_code=201)
def api_create_type(
    request: VehicleTypeCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    """Tambah tipe kendaraan baru."""
    return create_type(db, request)


@router.put("/vehicle-types/{type_id}", response_model=VehicleTypeOut)
def api_update_type(
    type_id: int,
    request: VehicleTypeUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    """Ubah tipe kendaraan."""
    return update_type(db, type_id, request)


@router.delete("/vehicle-types/{type_id}")
def api_delete_type(
    type_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    """Hapus tipe kendaraan."""
    return delete_type(db, type_id)


# ══════════════════════════════════════════════════════════════
# VEHICLE OWNER (admin, super_admin)
# ══════════════════════════════════════════════════════════════

@router.get("/vehicle-owners", response_model=VehicleOwnerListOut)
def api_list_owners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    plate_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    return list_owners(db, skip=skip, limit=limit, plate_number=plate_number)


@router.post("/vehicle-owners", response_model=VehicleOwnerOut, status_code=201)
def api_create_owner(
    request: VehicleOwnerCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    return create_owner(db, request)


@router.put("/vehicle-owners/{owner_id}", response_model=VehicleOwnerOut)
def api_update_owner(
    owner_id: int,
    request: VehicleOwnerUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    return update_owner(db, owner_id, request)


@router.delete("/vehicle-owners/{owner_id}")
def api_delete_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "admin")),
):
    return delete_owner(db, owner_id)


# ══════════════════════════════════════════════════════════════
# VEHICLE EVENTS & HISTORY (all authenticated)
# ══════════════════════════════════════════════════════════════

@router.get("/vehicles/events", response_model=VehicleEventListOut)
def api_list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    direction: Optional[str] = Query(None),
    plate_number: Optional[str] = Query(None),
    node_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return list_events(db, skip=skip, limit=limit, direction=direction, plate_number=plate_number, node_id=node_id)


@router.get("/vehicles/history", response_model=VehicleHistoryListOut)
def api_list_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    plate_number: Optional[str] = Query(None),
    node_id: Optional[str] = Query(None),
    is_inside: Optional[bool] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return list_history(
        db, skip=skip, limit=limit,
        plate_number=plate_number, node_id=node_id,
        is_inside=is_inside, date_from=date_from, date_to=date_to,
    )


@router.get("/vehicles/history/{history_id}", response_model=VehicleHistoryOut)
def api_get_history(
    history_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return get_history_detail(db, history_id)


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard/summary")
def api_dashboard_summary(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Ringkasan untuk dashboard monitoring."""
    from app.Models.VehicleEvent import VehicleEvent
    from app.Models.Node import Node
    from app.Models.VehicleHistory import VehicleHistory

    total_events = db.query(VehicleEvent).count()
    total_nodes = db.query(Node).count()
    online_nodes = db.query(Node).filter(Node.status == "online").count()
    vehicles_inside = db.query(VehicleHistory).filter(VehicleHistory.is_inside == True).count()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_events = db.query(VehicleEvent).filter(VehicleEvent.created_at >= today_start).count()

    return {
        "total_events": total_events,
        "today_events": today_events,
        "vehicles_inside": vehicles_inside,
        "total_nodes": total_nodes,
        "online_nodes": online_nodes,
        "offline_nodes": total_nodes - online_nodes,
    }
