"""
Entry point aplikasi Server.
Jalankan: uvicorn app.main:app --reload
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, SessionLocal
from app.routes import router as api_router

app = FastAPI(
    title="AutoGate UNS — Server",
    description="Server monitoring gerbang. Menerima data dari pos satpam.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (gambar dari node)
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
app.mount(
    settings.STORAGE_PUBLIC_PATH,
    StaticFiles(directory=settings.STORAGE_DIR),
    name="captures",
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    init_db()
    # Seed default super admin jika belum ada user
    from app.Http.Controllers.AuthController import seed_super_admin
    db = SessionLocal()
    try:
        seed_super_admin(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "service": "AutoGate UNS — Server", "version": "3.0.0"}