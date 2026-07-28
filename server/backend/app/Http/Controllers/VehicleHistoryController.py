"""
Controller untuk melihat history kendaraan (masuk+keluar) dan event.
"""
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.Models.VehicleEvent import VehicleEvent
from app.Models.VehicleHistory import VehicleHistory
from app.Models.VehicleOwner import VehicleOwner
from app.Models.Node import Node
from app.Http.Requests.VehicleHistoryRequest import (
    VehicleEventOut,
    VehicleEventListOut,
    VehicleHistoryOut,
    VehicleHistoryListOut,
)
from app.config import settings


def _to_event_out(event: VehicleEvent) -> VehicleEventOut:
    def _img_url(path):
        if not path:
            return None
        from pathlib import Path
        return f"{settings.STORAGE_PUBLIC_PATH.rstrip('/')}/{Path(path).name}"

    return VehicleEventOut(
        id=event.id,
        event_id=event.event_id,
        node_id=event.node_id,
        plate_number=event.plate_number,
        direction=event.direction,
        plate_image_url=_img_url(event.plate_image_path),
        scene_image_url=_img_url(event.scene_image_path),
        confidence=event.confidence,
        captured_at=event.captured_at.isoformat() if event.captured_at else None,
        created_at=event.created_at.isoformat() if event.created_at else None,
    )


def _to_history_out(history: VehicleHistory, entry_node_name=None, exit_node_name=None, owner_name=None) -> VehicleHistoryOut:
    return VehicleHistoryOut(
        id=history.id,
        plate_number=history.plate_number,
        entry_event_id=history.entry_event_id,
        exit_event_id=history.exit_event_id,
        entry_node_id=history.entry_node_id,
        exit_node_id=history.exit_node_id,
        entry_node_name=entry_node_name,
        exit_node_name=exit_node_name,
        entry_at=history.entry_at.isoformat() if history.entry_at else None,
        exit_at=history.exit_at.isoformat() if history.exit_at else None,
        is_inside=history.is_inside,
        owner_name=owner_name,
        created_at=history.created_at.isoformat() if history.created_at else None,
        updated_at=history.updated_at.isoformat() if history.updated_at else None,
    )


def list_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    direction: Optional[str] = None,
    plate_number: Optional[str] = None,
    node_id: Optional[str] = None,
) -> VehicleEventListOut:
    """GET /api/vehicles/events — daftar semua event masuk/keluar."""
    query = db.query(VehicleEvent)
    if direction:
        query = query.filter(VehicleEvent.direction == direction)
    if plate_number:
        query = query.filter(VehicleEvent.plate_number.ilike(f"%{plate_number}%"))
    if node_id:
        query = query.filter(VehicleEvent.node_id == node_id)
    query = query.order_by(VehicleEvent.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return VehicleEventListOut(total=total, items=[_to_event_out(e) for e in items])


def list_history(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    plate_number: Optional[str] = None,
    node_id: Optional[str] = None,
    is_inside: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> VehicleHistoryListOut:
    """GET /api/vehicles/history — daftar history kendaraan."""
    query = db.query(VehicleHistory)
    if plate_number:
        query = query.filter(VehicleHistory.plate_number.ilike(f"%{plate_number}%"))
    if node_id:
        query = query.filter(
            (VehicleHistory.entry_node_id == node_id) | (VehicleHistory.exit_node_id == node_id)
        )
    if is_inside is not None:
        query = query.filter(VehicleHistory.is_inside == is_inside)
    if date_from:
        query = query.filter(VehicleHistory.created_at >= date_from)
    if date_to:
        query = query.filter(VehicleHistory.created_at <= date_to)
    query = query.order_by(VehicleHistory.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()

    # Ambil nama node dan pemilik untuk setiap history
    node_cache = {}
    owner_cache = {}

    result = []
    for h in items:
        # Node names
        entry_node_name = None
        exit_node_name = None
        if h.entry_node_id:
            if h.entry_node_id not in node_cache:
                node = db.query(Node).filter(Node.id == h.entry_node_id).first()
                node_cache[h.entry_node_id] = node.name if node else h.entry_node_id
            entry_node_name = node_cache[h.entry_node_id]
        if h.exit_node_id:
            if h.exit_node_id not in node_cache:
                node = db.query(Node).filter(Node.id == h.exit_node_id).first()
                node_cache[h.exit_node_id] = node.name if node else h.exit_node_id
            exit_node_name = node_cache[h.exit_node_id]

        # Owner name
        owner_name = None
        if h.plate_number:
            if h.plate_number not in owner_cache:
                owner = db.query(VehicleOwner).filter(VehicleOwner.plate_number == h.plate_number).first()
                owner_cache[h.plate_number] = owner.owner_name if owner else None
            owner_name = owner_cache[h.plate_number]

        result.append(_to_history_out(h, entry_node_name, exit_node_name, owner_name))

    return VehicleHistoryListOut(total=total, items=result)


def get_history_detail(db: Session, history_id: int) -> VehicleHistoryOut:
    """GET /api/vehicles/history/{id} — detail 1 history."""
    h = db.query(VehicleHistory).filter(VehicleHistory.id == history_id).first()
    if not h:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="History tidak ditemukan")

    entry_node_name = None
    exit_node_name = None
    if h.entry_node_id:
        node = db.query(Node).filter(Node.id == h.entry_node_id).first()
        entry_node_name = node.name if node else h.entry_node_id
    if h.exit_node_id:
        node = db.query(Node).filter(Node.id == h.exit_node_id).first()
        exit_node_name = node.name if node else h.exit_node_id

    owner = db.query(VehicleOwner).filter(VehicleOwner.plate_number == h.plate_number).first()
    owner_name = owner.owner_name if owner else None

    return _to_history_out(h, entry_node_name, exit_node_name, owner_name)
