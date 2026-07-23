"""
Controller sinkronisasi — Pos Satpam.
"""
from app.Services.SyncService import sync_service


def get_sync_status() -> dict:
    """GET /api/sync/status — status sinkronisasi."""
    return sync_service.get_sync_status()


async def manual_sync() -> dict:
    """POST /api/sync/manual — trigger sync manual."""
    return await sync_service.manual_sync()
