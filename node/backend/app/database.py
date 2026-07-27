"""
Koneksi SQLite untuk Pos Satpam.
Menggunakan sqlite3 bawaan Python — tidak perlu driver tambahan.
"""
import sqlite3
from contextlib import contextmanager
from app.config import settings


def get_connection() -> sqlite3.Connection:
    """Buat koneksi SQLite baru. Row factory agar bisa akses kolom by name."""
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # performa lebih baik untuk concurrent read/write
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    """Context manager untuk koneksi DB. Auto-commit jika tidak ada error."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Buat semua tabel jika belum ada (dipanggil saat startup)."""
    conn = get_connection()
    cursor = conn.cursor()

    # Migrasi sederhana jika tabel vehicles sudah ada tapi belum punya kolom event_id
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicles';")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(vehicles);")
        columns = [col[1] for col in cursor.fetchall()]
        if "event_id" not in columns:
            cursor.execute("ALTER TABLE vehicles ADD COLUMN event_id TEXT;")

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            direction TEXT NOT NULL,
            plate_number TEXT NOT NULL,
            plate_image_path TEXT,
            scene_image_path TEXT,
            confidence REAL,
            captured_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            synced INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_vehicles_event_id ON vehicles(event_id);
        CREATE INDEX IF NOT EXISTS idx_vehicles_direction ON vehicles(direction);
        CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON vehicles(plate_number);
        CREATE INDEX IF NOT EXISTS idx_vehicles_synced ON vehicles(synced);

        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            retry_count INTEGER DEFAULT 0,
            last_attempt_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        );

        CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);

        CREATE TABLE IF NOT EXISTS relay_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel INTEGER NOT NULL,
            status INTEGER NOT NULL,
            triggered_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS device_status (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            camera_in_active INTEGER DEFAULT 0,
            camera_out_active INTEGER DEFAULT 0,
            relay_in_active INTEGER DEFAULT 0,
            relay_out_active INTEGER DEFAULT 0,
            last_camera_in_at TEXT,
            last_camera_out_at TEXT,
            last_relay_in_at TEXT,
            last_relay_out_at TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        );

        INSERT OR IGNORE INTO device_status (id) VALUES (1);
    """)

    conn.commit()
    conn.close()
