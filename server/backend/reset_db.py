"""
Reset database PostgreSQL — drop dan buat ulang database.
Tabel akan dibuat otomatis saat backend dijalankan (via init_db()).

Usage:
    python reset_db.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/autogatedb")

# Ambil nama database dari URL
db_name = db_url.rsplit("/", 1)[-1]

# URL untuk connect ke database 'postgres' (default) untuk drop/create db
base_url = db_url.rsplit("/", 1)[0] + "/postgres"

print(f"Database: {db_name}")

confirm = input(f"Drop dan buat ulang database '{db_name}'? (y/N): ").strip().lower()
if confirm != "y":
    print("Dibatalkan.")
    sys.exit(0)

engine = create_engine(base_url, isolation_level="AUTOCOMMIT")

with engine.connect() as conn:
    # Tutup semua koneksi aktif ke database
    conn.execute(text(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
          AND pid <> pg_backend_pid()
    """))

    # Drop database
    conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
    print(f"Database '{db_name}' di-drop.")

    # Buat ulang
    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    print(f"Database '{db_name}' dibuat ulang.")

engine.dispose()

print("Selesai. Jalankan backend server untuk membuat tabel secara otomatis.")
