"""
Konfigurasi untuk Pos Satpam (Node).
Semua nilai dibaca dari .env. Mendukung hot-reload.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load .env saat pertama kali
load_dotenv(ENV_PATH, override=True)


def _bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _getenv(key: str, default: str = "") -> str:
    """Baca env var. Dipanggil setiap kali diakses (hot-reload)."""
    return os.getenv(key, default)


class Settings:
    """Settings class yang re-read dari environment setiap kali diakses."""

    @property
    def NODE_ID(self) -> str:
        return _getenv("NODE_ID", "node-gerbang-depan")

    @property
    def NODE_NAME(self) -> str:
        return _getenv("NODE_NAME", "Gerbang Depan")

    @property
    def SQLITE_DB_PATH(self) -> str:
        return _getenv("SQLITE_DB_PATH", "./data/local.db")

    # ── Kamera MASUK ──
    @property
    def CAMERA_IN_HOST(self) -> str:
        return _getenv("CAMERA_IN_HOST", "192.168.1.64")

    @property
    def CAMERA_IN_USER(self) -> str:
        return _getenv("CAMERA_IN_USER", "admin")

    @property
    def CAMERA_IN_PASSWORD(self) -> str:
        return _getenv("CAMERA_IN_PASSWORD", "")

    @property
    def CAMERA_IN_CHANNEL(self) -> int:
        return int(_getenv("CAMERA_IN_CHANNEL", "1"))

    @property
    def CAMERA_IN_USE_HTTPS(self) -> bool:
        return _bool(_getenv("CAMERA_IN_USE_HTTPS"), False)

    @property
    def CAMERA_IN_INTERVAL(self) -> int:
        return int(_getenv("CAMERA_IN_INTERVAL", "1000"))

    # ── Kamera KELUAR ──
    @property
    def CAMERA_OUT_HOST(self) -> str:
        return _getenv("CAMERA_OUT_HOST", "192.168.1.65")

    @property
    def CAMERA_OUT_USER(self) -> str:
        return _getenv("CAMERA_OUT_USER", "admin")

    @property
    def CAMERA_OUT_PASSWORD(self) -> str:
        return _getenv("CAMERA_OUT_PASSWORD", "")

    @property
    def CAMERA_OUT_CHANNEL(self) -> int:
        return int(_getenv("CAMERA_OUT_CHANNEL", "1"))

    @property
    def CAMERA_OUT_USE_HTTPS(self) -> bool:
        return _bool(_getenv("CAMERA_OUT_USE_HTTPS"), False)

    @property
    def CAMERA_OUT_INTERVAL(self) -> int:
        return int(_getenv("CAMERA_OUT_INTERVAL", "1000"))

    # ── Kamera Umum ──
    @property
    def CAMERA_AUTH_TYPE(self) -> str:
        return _getenv("CAMERA_AUTH_TYPE", "digest")

    @property
    def CAMERA_TIMEOUT(self) -> int:
        return int(_getenv("CAMERA_TIMEOUT", "10"))

    @property
    def UNKNOWN_PLATE_VALUES(self) -> set:
        return {
            v.strip().lower()
            for v in _getenv(
                "UNKNOWN_PLATE_VALUES", "unknown,unknow,unrecognized,unrecognised,n/a,noplate,none,-"
            ).split(",")
            if v.strip()
        }

    # ── Storage ──
    @property
    def STORAGE_DIR(self) -> str:
        return _getenv("STORAGE_DIR", "./storage/captures")

    @property
    def STORAGE_PUBLIC_PATH(self) -> str:
        return _getenv("STORAGE_PUBLIC_PATH", "/storage/captures")

    # ── Modbus Relay ──
    @property
    def MODBUS_HOST(self) -> str:
        return _getenv("MODBUS_HOST", "192.168.1.200")

    @property
    def MODBUS_PORT(self) -> int:
        return int(_getenv("MODBUS_PORT", "502"))

    # ── Server (untuk sinkronisasi) ──
    @property
    def SERVER_URL(self) -> str:
        return _getenv("SERVER_URL", "http://localhost:8000")

    @property
    def SERVER_API_KEY(self) -> str:
        return _getenv("SERVER_API_KEY", "")

    @property
    def SYNC_INTERVAL(self) -> int:
        return int(_getenv("SYNC_INTERVAL", "30"))

    @property
    def HEARTBEAT_INTERVAL(self) -> int:
        return int(_getenv("HEARTBEAT_INTERVAL", "60"))

    # ── App ──
    @property
    def APP_HOST(self) -> str:
        return _getenv("APP_HOST", "0.0.0.0")

    @property
    def APP_PORT(self) -> int:
        return int(_getenv("APP_PORT", "3000"))


settings = Settings()

# Pastikan folder storage ada
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
