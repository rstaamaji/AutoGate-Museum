"""
Konfigurasi aplikasi. Mirip config/*.php di Laravel — semua nilai dibaca dari .env.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# cari .env di root folder backend/
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/autogatedb"
    )

    # Kamera - nilai default/fallback lama (dipakai kalau CAMERA_IN_* / CAMERA_OUT_* tidak diisi)
    CAMERA_HOST: str = os.getenv("CAMERA_HOST", "192.168.1.64")
    CAMERA_USER: str = os.getenv("CAMERA_USER", "admin")
    CAMERA_PASSWORD: str = os.getenv("CAMERA_PASSWORD", "")
    CAMERA_CHANNEL: int = int(os.getenv("CAMERA_CHANNEL", "1"))
    CAMERA_USE_HTTPS: bool = _bool(os.getenv("CAMERA_USE_HTTPS"), False)
    CAMERA_AUTH_TYPE: str = os.getenv("CAMERA_AUTH_TYPE", "digest")
    CAMERA_TIMEOUT: int = int(os.getenv("CAMERA_TIMEOUT", "10"))

    # Kamera MASUK (entry)
    CAMERA_IN_HOST: str = os.getenv("CAMERA_IN_HOST", CAMERA_HOST)
    CAMERA_IN_USER: str = os.getenv("CAMERA_IN_USER", CAMERA_USER)
    CAMERA_IN_PASSWORD: str = os.getenv("CAMERA_IN_PASSWORD", CAMERA_PASSWORD)
    CAMERA_IN_CHANNEL: int = int(os.getenv("CAMERA_IN_CHANNEL", str(CAMERA_CHANNEL)))
    CAMERA_IN_USE_HTTPS: bool = _bool(os.getenv("CAMERA_IN_USE_HTTPS"), CAMERA_USE_HTTPS)

    # Kamera KELUAR (exit)
    CAMERA_OUT_HOST: str = os.getenv("CAMERA_OUT_HOST", "192.168.1.65")
    CAMERA_OUT_USER: str = os.getenv("CAMERA_OUT_USER", CAMERA_USER)
    CAMERA_OUT_PASSWORD: str = os.getenv("CAMERA_OUT_PASSWORD", CAMERA_PASSWORD)
    CAMERA_OUT_CHANNEL: int = int(os.getenv("CAMERA_OUT_CHANNEL", "1"))
    CAMERA_OUT_USE_HTTPS: bool = _bool(os.getenv("CAMERA_OUT_USE_HTTPS"), CAMERA_USE_HTTPS)

    # Kalau kamera membaca plat tapi hasilnya "tidak terbaca", biasanya kamera
    # mengirim teks semacam ini di field licensePlate -> dianggap unknown & diabaikan.
    UNKNOWN_PLATE_VALUES: set = {
        v.strip().lower()
        for v in os.getenv(
            "UNKNOWN_PLATE_VALUES", "unknown,unknow,unrecognized,unrecognised,n/a,noplate,none,-"
        ).split(",")
        if v.strip()
    }

    # Storage
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage/captures")
    STORAGE_PUBLIC_PATH: str = os.getenv("STORAGE_PUBLIC_PATH", "/storage/captures")

    # Modbus Relay
    MODBUS_HOST: str = os.getenv("MODBUS_HOST", "192.168.1.200")
    MODBUS_PORT: int = int(os.getenv("MODBUS_PORT", "502"))

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    API_KEY: str = os.getenv("API_KEY", "")


settings = Settings()

# pastikan folder penyimpanan ada
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
