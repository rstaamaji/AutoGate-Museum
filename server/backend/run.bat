@echo off
REM Jalankan dari folder backend\: run.bat

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat

pip install -r requirements.txt

if not exist ".env" (
    copy .env.example .env
    echo File .env dibuat dari .env.example — sesuaikan dulu sebelum lanjut.
)

REM jalankan migration (butuh database sudah dibuat manual di PostgreSQL)
alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
