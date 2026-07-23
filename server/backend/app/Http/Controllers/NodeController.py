"""
Controller untuk manajemen node (pos satpam).
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.Models.Node import Node

# Batas waktu untuk menganggap node offline (3 menit tanpa heartbeat)
OFFLINE_THRESHOLD_MINUTES = 3

def ensure_utc(dt: datetime) -> datetime:
    """Pastikan datetime memiliki timezone UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def register_node(db: Session, node_id: str, name: str, location: str = None) -> dict:
    """Registrasi node baru atau update data existing."""
    node = db.query(Node).filter(Node.id == node_id).first()

    if node:
        node.name = name
        if location:
            node.location = location
        node.status = "online"
        node.last_seen_at = datetime.now(timezone.utc)
    else:
        node = Node(
            id=node_id,
            name=name,
            location=location,
            status="online",
            last_seen_at=datetime.now(timezone.utc),
        )
        db.add(node)

    db.commit()
    return {"success": True, "node_id": node_id, "message": "Node registered"}


def update_node_status(db: Session, node_id: str, status_data: dict) -> dict:
    """Update status perangkat node via heartbeat."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        node = Node(id=node_id, name=node_id, status="online")
        db.add(node)

    node.last_seen_at = datetime.now(timezone.utc)
    node.status = "online"
    node.camera_in_active = status_data.get("camera_in_active", False)
    node.camera_out_active = status_data.get("camera_out_active", False)
    node.relay_in_active = status_data.get("relay_in_active", False)
    node.relay_out_active = status_data.get("relay_out_active", False)

    db.commit()
    return {"success": True, "node_id": node_id}


def get_all_nodes(db: Session) -> list[dict]:
    """Ambil semua node + status. Auto-mark offline jika heartbeat expired."""
    nodes = db.query(Node).all()
    threshold = datetime.now(timezone.utc) - timedelta(
        minutes=OFFLINE_THRESHOLD_MINUTES
    )
    result = []

    for node in nodes:
        # Auto-mark offline jika tidak ada heartbeat
        if (
            node.last_seen_at
            and ensure_utc(node.last_seen_at) < threshold
            and node.status == "online"
        ):
            node.status = "offline"
            db.commit()

        result.append({
            "id": node.id,
            "name": node.name,
            "location": node.location,
            "status": node.status,
            "last_seen_at": node.last_seen_at.isoformat() if node.last_seen_at else None,
            "camera_in_active": node.camera_in_active,
            "camera_out_active": node.camera_out_active,
            "relay_in_active": node.relay_in_active,
            "relay_out_active": node.relay_out_active,
            "created_at": node.created_at.isoformat() if node.created_at else None,
        })

    return result


def get_node(db: Session, node_id: str) -> dict:
    """Ambil satu node by ID."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        return None

    threshold = datetime.now(timezone.utc) - timedelta(
        minutes=OFFLINE_THRESHOLD_MINUTES
    )
    if (
        node.last_seen_at
        and ensure_utc(node.last_seen_at) < threshold
        and node.status == "online"
    ):
        node.status = "offline"
        db.commit()

    return {
        "id": node.id,
        "name": node.name,
        "location": node.location,
        "status": node.status,
        "last_seen_at": node.last_seen_at.isoformat() if node.last_seen_at else None,
        "camera_in_active": node.camera_in_active,
        "camera_out_active": node.camera_out_active,
        "relay_in_active": node.relay_in_active,
        "relay_out_active": node.relay_out_active,
        "created_at": node.created_at.isoformat() if node.created_at else None,
    }
