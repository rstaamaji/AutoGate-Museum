"""
Controller untuk manajemen user (super_admin only).
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.Models.User import User
from app.Http.Controllers.AuthController import hash_password
from app.Http.Requests.UserRequest import (
    UserCreateRequest,
    UserUpdateRequest,
    UserOut,
    UserListOut,
)


def _to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
        updated_at=user.updated_at.isoformat() if user.updated_at else None,
    )


def list_users(db: Session) -> UserListOut:
    """GET /api/users — semua user."""
    users = db.query(User).order_by(User.id).all()
    return UserListOut(total=len(users), items=[_to_out(u) for u in users])


def create_user(db: Session, request: UserCreateRequest) -> UserOut:
    """POST /api/users — buat user baru."""
    # Cek username unik
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{request.username}' sudah digunakan",
        )

    user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role,
        name=request.name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_out(user)


def update_user(db: Session, user_id: int, request: UserUpdateRequest) -> UserOut:
    """PUT /api/users/{id} — update user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    if request.username is not None:
        # Cek username unik (kecuali user ini sendiri)
        existing = db.query(User).filter(User.username == request.username, User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{request.username}' sudah digunakan",
            )
        user.username = request.username

    if request.password is not None:
        user.password_hash = hash_password(request.password)

    if request.role is not None:
        user.role = request.role

    if request.name is not None:
        user.name = request.name

    if request.is_active is not None:
        user.is_active = request.is_active

    db.commit()
    db.refresh(user)
    return _to_out(user)


def delete_user(db: Session, user_id: int) -> dict:
    """DELETE /api/users/{id} — hapus user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    db.delete(user)
    db.commit()
    return {"success": True, "message": f"User '{user.username}' berhasil dihapus"}
