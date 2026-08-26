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
    from app.Models import User  # noqa: F401
    from app.Models import Node  # noqa: F401
    from app.Models import VehicleOwner  # noqa: F401
    from app.Models import Vehicle  # noqa: F401
    from app.Models import VehicleEvent  # noqa: F401
    from app.Models import VehicleHistory  # noqa: F401
<<<<<<< Updated upstream
    from app.Models import VehicleType  # noqa: F401
=======
    from app.Models import ParkingTicket  # noqa: F401
>>>>>>> Stashed changes

    Base.metadata.create_all(bind=engine)
    _link_orphan_vehicles()


def _link_orphan_vehicles():
    """Satu kali: link vehicle yang owner_id-nya NULL dengan owner yang plat-nya sama."""
    from app.Models.Vehicle import Vehicle
    from app.Models.VehicleOwner import VehicleOwner

    db = SessionLocal()
    try:
        orphans = db.query(Vehicle).filter(Vehicle.owner_id.is_(None)).all()
        if not orphans:
            return
        linked = 0
        for v in orphans:
            owner = db.query(VehicleOwner).filter(VehicleOwner.plate_number == v.plate_number).first()
            if owner:
                v.owner_id = owner.id
                linked += 1
        if linked:
            db.commit()
            print(f"[DB] Linked {linked} orphan vehicles ke owner")
    except Exception as e:
        print(f"[DB] Gagal link orphan vehicles: {e}")
        db.rollback()
    finally:
        db.close()
