import asyncio
import logging
from fastapi import HTTPException
from pymodbus.client import ModbusTcpClient

from app.Http.Requests.RelayRequest import RelayControlRequest, RelayControlResponse
from app.config import settings

logger = logging.getLogger(__name__)

class RelayController:
    @staticmethod
    def control(payload: RelayControlRequest) -> RelayControlResponse:
        """
        Mengontrol channel modbus relay menggunakan pymodbus.
        """
        try:
            client = ModbusTcpClient(settings.MODBUS_HOST, port=settings.MODBUS_PORT)
            
            if not client.connect():
                raise HTTPException(
                    status_code=503,
                    detail=f"Gagal terhubung ke Modbus Relay di {settings.MODBUS_HOST}:{settings.MODBUS_PORT}"
                )
            
            # Alamat channel Modbus umumnya 0-indexed (channel 1 = address 0)
            # Jika hardware Anda menggunakan alamat sesuai dengan nomor channel, 
            # hapus pengurangan - 1 di bawah ini.
            address = payload.channel - 1
            if address < 0:
                address = 0
                
            # Tulis coil (ON = True/1, OFF = False/0)
            result = client.write_coil(address, payload.status, slave=1)
            
            client.close()
            
            if result.isError():
                raise HTTPException(
                    status_code=500,
                    detail=f"Gagal menulis ke channel {payload.channel} Modbus."
                )
            
            return RelayControlResponse(
                success=True,
                message=f"Berhasil mengubah channel {payload.channel} menjadi {'ON' if payload.status else 'OFF'}",
                channel=payload.channel,
                status=payload.status
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Modbus error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")

    @staticmethod
    async def open_and_close_delayed(channel: int, delay_seconds: int = 15):
        """
        Buka relay, tunggu sekian detik, lalu tutup kembali.
        Digunakan sebagai background task.
        """
        try:
            logger.info(f"Membuka relay channel {channel}...")
            RelayController.control(RelayControlRequest(channel=channel, status=True))
            
            await asyncio.sleep(delay_seconds)
            
            logger.info(f"Menutup relay channel {channel} setelah {delay_seconds} detik...")
            RelayController.control(RelayControlRequest(channel=channel, status=False))
        except Exception as e:
            logger.error(f"Gagal menjalankan auto-close relay pada channel {channel}: {str(e)}")

