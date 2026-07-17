"""
Koneksi DB, mirip config/database.php di Laravel.
Migration sesungguhnya dijalankan lewat Alembic (lihat database/migrations),
tapi tetap disediakan init_db() sebagai jalan pintas untuk development.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency FastAPI, mirip DI Eloquent Model di controller Laravel."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Buat semua tabel dari Models langsung (shortcut dev, tanpa Alembic)."""
    from app.Models import Vehicle  # noqa: F401  (registrasi model ke Base.metadata)

    Base.metadata.create_all(bind=engine)
