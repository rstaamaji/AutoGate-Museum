"""
Model RelayLog — log aktivitas relay (audit trail).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RelayLog:
    id: Optional[int] = None
    channel: int = 0
    status: int = 0  # 0 = OFF, 1 = ON
    triggered_by: Optional[str] = None  # "auto" / "manual"
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "RelayLog":
        return cls(
            id=row["id"],
            channel=row["channel"],
            status=row["status"],
            triggered_by=row["triggered_by"],
            created_at=row["created_at"],
        )
