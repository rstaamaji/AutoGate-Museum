"""
Autentikasi & otorisasi — Server.
"""
from typing import Optional

from fastapi import HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.Models.User import User
from app.Models.Node import Node

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


# ── JWT ──

def create_access_token(data: dict) -> str:
    """Buat JWT token."""
    from datetime import datetime, timedelta, timezone
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT token dari Authorization header dan return user."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak ditemukan",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token kosong")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
        user_id = int(user_id)
    except (JWTError, ValueError, Exception) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token tidak valid: {e}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User nonaktif")

    return user


def require_role(*allowed_roles: str):
    """Dependency factory: batasi endpoint berdasarkan role."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Role yang diizinkan: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker


# ── Node API Key ──

async def verify_node_api_key(
    x_api_key: str = Security(api_key_scheme),
    db: Session = Depends(get_db),
) -> Node:
    """Verifikasi API key node. Return Node object jika valid."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key node tidak ditemukan",
        )
    print(f"[NODE AUTH] Received X-API-Key: {x_api_key[:20]}..." if len(x_api_key) > 20 else f"[NODE AUTH] Received X-API-Key: {x_api_key}")
    node = db.query(Node).filter(Node.api_key == x_api_key).first()
    if not node:
        # Debug: tampilkan semua API key yang ada
        all_nodes = db.query(Node).all()
        for n in all_nodes:
            print(f"[NODE AUTH] Registered node: {n.id} key={n.api_key[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key node tidak valid",
        )
    print(f"[NODE AUTH] Node authenticated: {node.id} ({node.name})")
    return node
