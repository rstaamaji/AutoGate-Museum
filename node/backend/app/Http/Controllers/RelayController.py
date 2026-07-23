"""
Controller relay (Modbus) — Pos Satpam.
Kontrol buka/tutup gate secara lokal.
"""
import asyncio
import logging
from datetime import datetime

from fastapi import HTTPException
from pymodbus.client import ModbusTcpClient

from app.Http.Requests.RelayRequest import RelayControlRequest, RelayControlResponse
from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)


class RelayController:
    @staticmethod
    def control(payload: RelayControlRequest, triggered_by: str = "manual") -> RelayControlResponse:
        """Kontrol channel modbus relay."""
        try:
            client = ModbusTcpClient(settings.MODBUS_HOST, port=settings.MODBUS_PORT)

            if not client.connect():
                raise HTTPException(
                    status_code=503,
                    detail=f"Gagal terhubung ke Modbus Relay di {settings.MODBUS_HOST}:{settings.MODBUS_PORT}"
                )

            address = max(payload.channel - 1, 0)
            result = client.write_coil(address, payload.status)
            client.close()

            if result.isError():
                raise HTTPException(
                    status_code=500,
                    detail=f"Gagal menulis ke channel {payload.channel} Modbus."
                )

            # Simpan log relay
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO relay_logs (channel, status, triggered_by) VALUES (?, ?, ?)",
                    (payload.channel, int(payload.status), triggered_by),
                )

                # Update device_status
                now = datetime.utcnow().isoformat()
                if payload.channel == 1:
                    conn.execute(
                        "UPDATE device_status SET relay_in_active = ?, last_relay_in_at = ?, updated_at = ? WHERE id = 1",
                        (int(payload.status), now, now),
                    )
                elif payload.channel == 2:
                    conn.execute(
                        "UPDATE device_status SET relay_out_active = ?, last_relay_out_at = ?, updated_at = ? WHERE id = 1",
                        (int(payload.status), now, now),
                    )

            return RelayControlResponse(
                success=True,
                message=f"Channel {payload.channel} → {'ON' if payload.status else 'OFF'}",
                channel=payload.channel,
                status=payload.status,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Modbus error: {e}")
            raise HTTPException(status_code=500, detail=f"Error internal: {e}")

    @staticmethod
    async def open_and_close_delayed(channel: int, delay_seconds: int = 15):
        """Buka gate (trigger buka 1s), tunggu, tutup gate (trigger tutup 1s). Background task."""
        try:
            # Channel buka adalah `channel` (1 untuk Masuk, 4 untuk Keluar)
            # Channel tutup adalah `channel + 1` (2 untuk Masuk, 5 untuk Keluar)
            close_channel = channel + 1

            logger.info(f"Membuka gate (Trigger channel {channel} ON selama 1s)...")
            RelayController.control(
                RelayControlRequest(channel=channel, status=True),
                triggered_by="auto",
            )

            await asyncio.sleep(1)

            RelayController.control(
                RelayControlRequest(channel=channel, status=False),
                triggered_by="auto",
            )

            logger.info(f"Menunggu {delay_seconds} detik sebelum menutup gate...")
            await asyncio.sleep(delay_seconds)

            logger.info(f"Menutup gate (Trigger channel {close_channel} ON selama 1s)...")
            RelayController.control(
                RelayControlRequest(channel=close_channel, status=True),
                triggered_by="auto",
            )

            await asyncio.sleep(1)

            RelayController.control(
                RelayControlRequest(channel=close_channel, status=False),
                triggered_by="auto",
            )
        except Exception as e:
            logger.error(f"Gagal auto-close relay untuk gate {channel}: {e}")
