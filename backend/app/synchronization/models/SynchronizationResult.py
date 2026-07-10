from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SynchronizationResult:
    """
    Operational result returned by SynchronizationEngine.

    This object represents one complete synchronization execution.
    """

    provider_name: str

    status: str = "success"

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed_at: datetime | None = None

    collected: dict[str, int] = field(default_factory=dict)

    normalized: dict[str, int] = field(default_factory=dict)

    reconciled: dict[str, int] = field(default_factory=dict)

    created: dict[str, int] = field(default_factory=dict)

    updated: dict[str, int] = field(default_factory=dict)

    skipped: dict[str, int] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def complete(self):
        self.completed_at = datetime.now(timezone.utc)
        return self

    @property
    def duration_seconds(self) -> float | None:
        if self.completed_at is None:
            return None

        return round(
            (
                self.completed_at
                - self.started_at
            ).total_seconds(),
            3,
        )

    def to_dict(self):
        return {
            "provider": self.provider_name,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "duration_seconds": self.duration_seconds,
            "collected": self.collected,
            "normalized": self.normalized,
            "reconciled": self.reconciled,
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "warnings": self.warnings,
            "errors": self.errors,
            "metadata": self.metadata,
        }