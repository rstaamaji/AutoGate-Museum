#!/usr/bin/env bash
# Jalankan dari folder backend/: ./run.sh
# Di Windows, jalankan run.bat, atau pakai script ini lewat Git Bash / WSL.
set -e

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate

pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "File .env dibuat dari .env.example — sesuaikan dulu sebelum lanjut."
fi

# jalankan migration (butuh database sudah dibuat manual di PostgreSQL)
alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
