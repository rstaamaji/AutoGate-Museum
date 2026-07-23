"""
Model DeviceStatus — status terakhir perangkat (kamera & relay).
Single-row table (id selalu = 1).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceStatus:
    camera_in_active: int = 0
    camera_out_active: int = 0
    relay_in_active: int = 0
    relay_out_active: int = 0
    last_camera_in_at: Optional[str] = None
    last_camera_out_at: Optional[str] = None
    last_relay_in_at: Optional[str] = None
    last_relay_out_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "DeviceStatus":
        return cls(
            camera_in_active=row["camera_in_active"],
            camera_out_active=row["camera_out_active"],
            relay_in_active=row["relay_in_active"],
            relay_out_active=row["relay_out_active"],
            last_camera_in_at=row["last_camera_in_at"],
            last_camera_out_at=row["last_camera_out_at"],
            last_relay_in_at=row["last_relay_in_at"],
            last_relay_out_at=row["last_relay_out_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "camera_in_active": bool(self.camera_in_active),
            "camera_out_active": bool(self.camera_out_active),
            "relay_in_active": bool(self.relay_in_active),
            "relay_out_active": bool(self.relay_out_active),
            "last_camera_in_at": self.last_camera_in_at,
            "last_camera_out_at": self.last_camera_out_at,
            "last_relay_in_at": self.last_relay_in_at,
            "last_relay_out_at": self.last_relay_out_at,
            "updated_at": self.updated_at,
        }
