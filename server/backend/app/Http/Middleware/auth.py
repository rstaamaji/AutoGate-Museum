"""
Mirip app/Http/Middleware/Authenticate.php — dependency sederhana berbasis API key.
Aktif hanya kalau API_KEY diisi di .env. Kalau kosong, semua request lolos (dev mode).

Cara pakai di route:
    @router.get("/plates", dependencies=[Depends(verify_api_key)])
"""
from fastapi import Header, HTTPException, status

from app.config import settings


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if not settings.API_KEY:
        return  # proteksi dimatikan kalau API_KEY tidak diset
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key tidak valid atau tidak diisi (header X-API-Key)",
        )
