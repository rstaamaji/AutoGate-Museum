"""
Service sinkronisasi data dari Pos Satpam ke Server.
Background task yang berjalan terus-menerus:
  - Cek koneksi ke server setiap SYNC_INTERVAL detik
  - Kirim data pending dari sync_queue ke POST /api/sync/events
  - Kirim heartbeat + status perangkat
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

import httpx

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self):
        self._running = False
        self._server_online = False

    @property
    def server_online(self) -> bool:
        return self._server_online

    async def start(self):
        """Mulai background sync loop."""
        self._running = True
        logger.info(
            f"SyncService started — server: {settings.SERVER_URL}, "
            f"interval: {settings.SYNC_INTERVAL}s"
        )

        while self._running:
            try:
                # Cek koneksi server
                self._server_online = await self._check_server()

                if self._server_online:
                    # Kirim data pending
                    await self._sync_pending()

            except Exception as e:
                logger.error(f"SyncService error: {e}")
                self._server_online = False

            await asyncio.sleep(settings.SYNC_INTERVAL)

    async def stop(self):
        """Stop background sync."""
        self._running = False
        logger.info("SyncService stopped")

    async def _check_server(self) -> bool:
        """Ping server + update last_seen_at. Return True jika bisa dihubungi."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(
                    f"{settings.SERVER_URL}/api/nodes/ping",
                    headers=self._auth_headers(),
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def _sync_pending(self):
        """Kirim semua data pending dari sync_queue ke server."""
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM sync_queue WHERE status = 'pending' ORDER BY id ASC LIMIT 50"
            ).fetchall()

        if not rows:
            return

        logger.info(f"Syncing {len(rows)} pending items...")

        for row in rows:
            queue_id = row["id"]
            vehicle_id = row["vehicle_id"]
            payload_str = row["payload"]

            try:
                payload = json.loads(payload_str)
                success = await self._send_event_data(payload)

                if success:
                    with get_db() as conn:
                        conn.execute(
                            "UPDATE sync_queue SET status = 'sent', last_attempt_at = ? WHERE id = ?",
                            (datetime.utcnow().isoformat(), queue_id),
                        )
                        conn.execute(
                            "UPDATE vehicles SET synced = 1 WHERE id = ?",
                            (vehicle_id,),
                        )
                    logger.info(f"Synced vehicle_id={vehicle_id}")
                else:
                    self._mark_retry(queue_id, row["retry_count"])

            except Exception as e:
                logger.error(f"Sync error for vehicle_id={vehicle_id}: {e}")
                self._mark_retry(queue_id, row["retry_count"])

    async def _send_event_data(self, payload: dict) -> bool:
        """Kirim satu event kendaraan ke server (POST /api/sync/events)."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{settings.SERVER_URL}/api/sync/events",
                    json=payload,
                    headers=self._auth_headers(),
                )
                return resp.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"Failed to send event data: {e}")
            return False

    def _mark_retry(self, queue_id: int, current_retry: int):
        """Tandai item untuk retry."""
        new_status = "failed" if current_retry >= 10 else "pending"
        with get_db() as conn:
            conn.execute(
                "UPDATE sync_queue SET status = ?, retry_count = ?, last_attempt_at = ? WHERE id = ?",
                (new_status, current_retry + 1, datetime.utcnow().isoformat(), queue_id),
            )

    def _auth_headers(self) -> dict:
        """Header autentikasi untuk komunikasi ke server (node API key)."""
        headers = {"Content-Type": "application/json"}
        if settings.SERVER_API_KEY:
            headers["X-API-Key"] = settings.SERVER_API_KEY
        return headers

    def get_sync_status(self) -> dict:
        """Ambil status sinkronisasi saat ini."""
        with get_db() as conn:
            pending = conn.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'"
            ).fetchone()[0]
            sent = conn.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE status = 'sent'"
            ).fetchone()[0]
            failed = conn.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE status = 'failed'"
            ).fetchone()[0]

        return {
            "server_online": self._server_online,
            "pending": pending,
            "sent": sent,
            "failed": failed,
        }

    async def manual_sync(self) -> dict:
        """Trigger manual sync dari endpoint."""
        if not self._server_online:
            self._server_online = await self._check_server()

        if not self._server_online:
            return {"success": False, "message": "Server tidak bisa dihubungi"}

        await self._sync_pending()
        status = self.get_sync_status()
        return {"success": True, "message": "Sync selesai", **status}


# Singleton instance
sync_service = SyncService()
