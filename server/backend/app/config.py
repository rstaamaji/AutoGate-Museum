"""
Konfigurasi aplikasi Server — monitoring only.
Tidak ada setting kamera/relay (itu di pos satpam).
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

    # Auth
    API_KEY: str = os.getenv("API_KEY", "")

    # Storage (untuk gambar yang dikirim dari node)
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage/captures")
    STORAGE_PUBLIC_PATH: str = os.getenv("STORAGE_PUBLIC_PATH", "/storage/captures")

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))


settings = Settings()

Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
