"""
Konfigurasi untuk Pos Satpam (Node).
Semua nilai dibaca dari .env.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # ── Node Identity ──
    NODE_ID: str = os.getenv("NODE_ID", "node-gerbang-depan")
    NODE_NAME: str = os.getenv("NODE_NAME", "Gerbang Depan")

    # ── SQLite ──
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "./data/local.db")

    # ── Kamera MASUK ──
    CAMERA_IN_HOST: str = os.getenv("CAMERA_IN_HOST", "192.168.1.64")
    CAMERA_IN_USER: str = os.getenv("CAMERA_IN_USER", "admin")
    CAMERA_IN_PASSWORD: str = os.getenv("CAMERA_IN_PASSWORD", "")
    CAMERA_IN_CHANNEL: int = int(os.getenv("CAMERA_IN_CHANNEL", "1"))
    CAMERA_IN_USE_HTTPS: bool = _bool(os.getenv("CAMERA_IN_USE_HTTPS"), False)

    # ── Kamera KELUAR ──
    CAMERA_OUT_HOST: str = os.getenv("CAMERA_OUT_HOST", "192.168.1.65")
    CAMERA_OUT_USER: str = os.getenv("CAMERA_OUT_USER", "admin")
    CAMERA_OUT_PASSWORD: str = os.getenv("CAMERA_OUT_PASSWORD", "")
    CAMERA_OUT_CHANNEL: int = int(os.getenv("CAMERA_OUT_CHANNEL", "1"))
    CAMERA_OUT_USE_HTTPS: bool = _bool(os.getenv("CAMERA_OUT_USE_HTTPS"), False)

    # ── Kamera Umum ──
    CAMERA_AUTH_TYPE: str = os.getenv("CAMERA_AUTH_TYPE", "digest")
    CAMERA_TIMEOUT: int = int(os.getenv("CAMERA_TIMEOUT", "10"))

    UNKNOWN_PLATE_VALUES: set = {
        v.strip().lower()
        for v in os.getenv(
            "UNKNOWN_PLATE_VALUES", "unknown,unknow,unrecognized,unrecognised,n/a,noplate,none,-"
        ).split(",")
        if v.strip()
    }

    # ── Storage ──
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage/captures")
    STORAGE_PUBLIC_PATH: str = os.getenv("STORAGE_PUBLIC_PATH", "/storage/captures")

    # ── Modbus Relay ──
    MODBUS_HOST: str = os.getenv("MODBUS_HOST", "192.168.1.200")
    MODBUS_PORT: int = int(os.getenv("MODBUS_PORT", "502"))

    # ── Server (untuk sinkronisasi) ──
    SERVER_URL: str = os.getenv("SERVER_URL", "http://localhost:8000")
    SERVER_API_KEY: str = os.getenv("SERVER_API_KEY", "")
    SYNC_INTERVAL: int = int(os.getenv("SYNC_INTERVAL", "30"))  # detik
    HEARTBEAT_INTERVAL: int = int(os.getenv("HEARTBEAT_INTERVAL", "60"))  # detik

    # ── App ──
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "3000"))


settings = Settings()

# Pastikan folder storage ada
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
