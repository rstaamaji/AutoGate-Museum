"""
Entry point aplikasi, mirip public/index.php + bootstrap/app.php di Laravel.
Jalankan dengan: uvicorn app.main:app --reload
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes import router as api_router

app = FastAPI(
    title="ANPR Backend",
    description="Backend FastAPI untuk mencatat plat nomor kendaraan dari kamera Hikvision ANPR.",
    version="1.0.0",
)

# CORS - longgarkan sesuai kebutuhan frontend kamu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# expose folder gambar hasil capture, mis. http://localhost:8000/storage/captures/xxx.jpg
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
app.mount(
    settings.STORAGE_PUBLIC_PATH,
    StaticFiles(directory=settings.STORAGE_DIR),
    name="captures",
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    # Shortcut dev: buat tabel otomatis kalau belum ada.
    # Untuk production, pakai `alembic upgrade head` (lihat database/migrations).
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "ANPR Backend"}
