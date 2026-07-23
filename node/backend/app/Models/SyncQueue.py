"""
Model SyncQueue — antrian data yang belum terkirim ke server.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SyncQueue:
    id: Optional[int] = None
    vehicle_id: int = 0
    payload: str = ""  # JSON string
    status: str = "pending"  # pending / sent / failed
    retry_count: int = 0
    last_attempt_at: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "SyncQueue":
        return cls(
            id=row["id"],
            vehicle_id=row["vehicle_id"],
            payload=row["payload"],
            status=row["status"],
            retry_count=row["retry_count"],
            last_attempt_at=row["last_attempt_at"],
            created_at=row["created_at"],
        )
