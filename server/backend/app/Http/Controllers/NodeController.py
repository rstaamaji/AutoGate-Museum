"""
Controller untuk manajemen node (pos satpam).
Auto-generate UUID dan API key saat membuat node baru.
"""
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.Models.Node import Node
from app.Http.Requests.NodeRequest import (
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeOut,
    NodeListOut,
)

# Batas waktu untuk menganggap node offline (3 menit tanpa heartbeat)
OFFLINE_THRESHOLD_MINUTES = 3


def ensure_utc(dt: datetime) -> datetime:
    """Pastikan datetime memiliki timezone UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _generate_api_key() -> str:
    """Generate random API key 64 karakter hex."""
    return secrets.token_hex(32)


def _to_out(node: Node) -> NodeOut:
    return NodeOut(
        id=node.id,
        name=node.name,
        api_key=node.api_key,
        location=node.location,
        status=node.status,
        last_seen_at=node.last_seen_at.isoformat() if node.last_seen_at else None,
        camera_in_active=node.camera_in_active,
        camera_out_active=node.camera_out_active,
        relay_in_active=node.relay_in_active,
        relay_out_active=node.relay_out_active,
        created_at=node.created_at.isoformat() if node.created_at else None,
    )


def create_node(db: Session, request: NodeCreateRequest) -> NodeOut:
    """POST /api/nodes — buat node baru dengan auto UUID + API key."""
    node_id = str(uuid.uuid4())
    api_key = _generate_api_key()

    node = Node(
        id=node_id,
        name=request.name,
        api_key=api_key,
        location=request.location,
        status="offline",
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return _to_out(node)


def list_nodes(db: Session) -> NodeListOut:
    """GET /api/nodes — semua node + API key + auto-mark offline."""
    nodes = db.query(Node).order_by(Node.created_at.desc()).all()
    threshold = datetime.now(timezone.utc) - timedelta(minutes=OFFLINE_THRESHOLD_MINUTES)

    result = []
    for node in nodes:
        if (
            node.last_seen_at
            and ensure_utc(node.last_seen_at) < threshold
            and node.status == "online"
        ):
            node.status = "offline"

        result.append(_to_out(node))

    db.commit()
    return NodeListOut(total=len(result), items=result)


def get_node(db: Session, node_id: str) -> NodeOut:
    """GET /api/nodes/{id} — detail satu node."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node tidak ditemukan")

    threshold = datetime.now(timezone.utc) - timedelta(minutes=OFFLINE_THRESHOLD_MINUTES)
    if (
        node.last_seen_at
        and ensure_utc(node.last_seen_at) < threshold
        and node.status == "online"
    ):
        node.status = "offline"
        db.commit()

    return _to_out(node)


def update_node(db: Session, node_id: str, request: NodeUpdateRequest) -> NodeOut:
    """PUT /api/nodes/{id} — update nama/lokasi node."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node tidak ditemukan")

    if request.name is not None:
        node.name = request.name
    if request.location is not None:
        node.location = request.location

    db.commit()
    db.refresh(node)
    return _to_out(node)


def delete_node(db: Session, node_id: str) -> dict:
    """DELETE /api/nodes/{id} — hapus node."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node tidak ditemukan")

    db.delete(node)
    db.commit()
    return {"success": True, "message": f"Node '{node.name}' berhasil dihapus"}


def update_node_status(db: Session, node: Node, status_data: dict) -> dict:
    """Update status perangkat node via heartbeat (dipanggil dari node)."""
    node.last_seen_at = datetime.now(timezone.utc)
    node.status = "online"
    node.camera_in_active = status_data.get("camera_in_active", False)
    node.camera_out_active = status_data.get("camera_out_active", False)
    node.relay_in_active = status_data.get("relay_in_active", False)
    node.relay_out_active = status_data.get("relay_out_active", False)

    db.commit()
    return {"success": True, "node_id": node.id}
