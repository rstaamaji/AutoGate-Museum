"""
Entry point aplikasi Pos Satpam — FastAPI + SQLite.
Jalankan: uvicorn app.main:app --host 0.0.0.0 --port 3000
"""
import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes import router as api_router
from app.Services.SyncService import sync_service
from app.Http.Controllers.StatusController import refresh_camera_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoGate UNS — Pos Satpam",
    description="Backend untuk pos satpam gerbang. Offline-first, SQLite lokal.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (gambar capture)
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
app.mount(
    settings.STORAGE_PUBLIC_PATH,
    StaticFiles(directory=settings.STORAGE_DIR),
    name="captures",
)

app.include_router(api_router)


@app.on_event("startup")
async def on_startup():
    # Buat tabel SQLite jika belum ada
    init_db()
    logger.info("SQLite database initialized")

    # Mulai background sync task
    asyncio.create_task(sync_service.start())
    logger.info("Background sync task started")

    # Refresh status kamera pertama kali
    try:
        refresh_camera_status()
        logger.info("Camera status refreshed")
    except Exception as e:
        logger.warning(f"Could not refresh camera status: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    await sync_service.stop()


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "AutoGate UNS — Pos Satpam",
        "node_id": settings.NODE_ID,
        "node_name": settings.NODE_NAME,
    }
