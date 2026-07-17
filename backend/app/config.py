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

    # Kamera
    CAMERA_HOST: str = os.getenv("CAMERA_HOST", "192.168.1.64")
    CAMERA_USER: str = os.getenv("CAMERA_USER", "admin")
    CAMERA_PASSWORD: str = os.getenv("CAMERA_PASSWORD", "")
    CAMERA_CHANNEL: int = int(os.getenv("CAMERA_CHANNEL", "1"))
    CAMERA_USE_HTTPS: bool = _bool(os.getenv("CAMERA_USE_HTTPS"), False)
    CAMERA_AUTH_TYPE: str = os.getenv("CAMERA_AUTH_TYPE", "digest")
    CAMERA_TIMEOUT: int = int(os.getenv("CAMERA_TIMEOUT", "10"))

    # Storage
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage/captures")
    STORAGE_PUBLIC_PATH: str = os.getenv("STORAGE_PUBLIC_PATH", "/storage/captures")

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    API_KEY: str = os.getenv("API_KEY", "")


settings = Settings()

# pastikan folder penyimpanan ada
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
