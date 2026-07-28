"""
Model Node — data pos satpam yang terdaftar di server.
Setiap node punya API key unik untuk autentikasi node → server.
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String(50), primary_key=True)  # UUID, auto-generate di backend
    name = Column(String(100), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, index=True)  # auto-generate random hex
    location = Column(String(255), nullable=True)
    status = Column(String(20), default="offline")  # online / offline
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    # Status perangkat dari node
    camera_in_active = Column(Boolean, default=False)
    camera_out_active = Column(Boolean, default=False)
    relay_in_active = Column(Boolean, default=False)
    relay_out_active = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
