"""
Konfigurasi aplikasi Server.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # Database PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/autogatedb"
    )

    # Auth — JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # Auth — API key untuk node → server (legacy, sekarang per-node)
    API_KEY: str = os.getenv("API_KEY", "")

    # Default super admin (seed saat startup pertama)
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "superadmin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    # Storage (untuk gambar yang dikirim dari node)
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage/captures")
    STORAGE_PUBLIC_PATH: str = os.getenv("STORAGE_PUBLIC_PATH", "/storage/captures")

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    #midtrans
    TARIF_KARCIS: int = int(os.getenv("TARIF_KARCIS", "5000"))
    MIDTRANS_SERVER_KEY: str = os.getenv("MIDTRANS_SERVER_KEY", "")
    MIDTRANS_CLIENT_KEY: str = os.getenv("MIDTRANS_CLIENT_KEY", "")
    MIDTRANS_IS_PRODUCTION: bool = os.getenv(
    "MIDTRANS_IS_PRODUCTION", "false"
    ).lower() == "true"


settings = Settings()

Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
