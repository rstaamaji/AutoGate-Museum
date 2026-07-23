"""
Middleware autentikasi — Pos Satpam.
API key untuk melindungi endpoint (opsional, aktif jika NODE_API_KEY diisi).
"""
from fastapi import Header, HTTPException, status
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

NODE_API_KEY = os.getenv("NODE_API_KEY", "")


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if not NODE_API_KEY:
        return  # proteksi dimatikan
    if x_api_key != NODE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key tidak valid (header X-API-Key)",
        )
