"""
Controller autentikasi — login, info user.
"""
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.Models.User import User
from app.Http.Middleware.auth import create_access_token
from app.Http.Requests.AuthRequest import LoginRequest, LoginResponse, UserInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password dengan bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password terhadap hash."""
    return pwd_context.verify(plain_password, hashed_password)


def login(db: Session, request: LoginRequest) -> LoginResponse:
    """
    Login dengan username + password.
    Return JWT token + info user.
    """
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User nonaktif. Hubungi super admin.",
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
        ),
    )


def get_me(current_user: User) -> UserInfo:
    """Return info user dari token."""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
    )


def seed_super_admin(db: Session):
    """
    Seed default super admin saat startup pertama.
    Hanya dijalankan jika belum ada user sama sekali.
    """
    from app.config import settings

    user_count = db.query(User).count()
    if user_count > 0:
        return  # sudah ada user, skip

    admin = User(
        username=settings.DEFAULT_ADMIN_USERNAME,
        password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
        role="super_admin",
        name="Super Administrator",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print(f"[SEED] Super admin '{settings.DEFAULT_ADMIN_USERNAME}' berhasil dibuat.")
