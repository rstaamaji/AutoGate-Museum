"""
Koneksi DB PostgreSQL — Server.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Buat semua tabel dari Models langsung (shortcut dev)."""
    from app.Models import Vehicle  # noqa: F401
    from app.Models import Node  # noqa: F401

    Base.metadata.create_all(bind=engine)
