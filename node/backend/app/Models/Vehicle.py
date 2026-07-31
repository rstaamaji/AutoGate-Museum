"""
Model Vehicle untuk SQLite — Pos Satpam.
Data kendaraan yang tercapture oleh kamera ANPR.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Vehicle:
    id: Optional[int] = None
    event_id: str = ""  # UUID, dibuat saat capture
    direction: str = ""  # "masuk" / "keluar"
    plate_number: str = ""
    plate_image_path: Optional[str] = None
    scene_image_path: Optional[str] = None
    confidence: Optional[float] = None
    captured_at: Optional[str] = None
    created_at: Optional[str] = None
    synced: int = 0  # 0 = belum, 1 = sudah
    rfid_uid: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Vehicle":
        """Buat Vehicle dari sqlite3.Row."""
        return cls(
            id=row["id"],
            event_id=row["event_id"],
            direction=row["direction"],
            plate_number=row["plate_number"],
            plate_image_path=row["plate_image_path"],
            scene_image_path=row["scene_image_path"],
            confidence=row["confidence"],
            captured_at=row["captured_at"],
            created_at=row["created_at"],
            synced=row["synced"],
            rfid_uid=row["rfid_uid"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "direction": self.direction,
            "plate_number": self.plate_number,
            "plate_image_path": self.plate_image_path,
            "scene_image_path": self.scene_image_path,
            "confidence": self.confidence,
            "captured_at": self.captured_at,
            "created_at": self.created_at,
            "synced": bool(self.synced),
            "rfid_uid": self.rfid_uid,
        }
