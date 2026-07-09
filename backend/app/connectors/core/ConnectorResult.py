from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ConnectorResult:
    """
    Standard result returned by connector provider operations.
    """

    provider_name: str
    operation: str
    success: bool
    message: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    records_collected: int = 0
    records_normalized: int = 0
    records_synchronized: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def complete(self) -> "ConnectorResult":
        self.completed_at = datetime.now(timezone.utc)
        return self

    def add_error(self, error: str) -> "ConnectorResult":
        self.errors.append(error)
        self.success = False
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "operation": self.operation,
            "success": self.success,
            "message": self.message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "records_collected": self.records_collected,
            "records_normalized": self.records_normalized,
            "records_synchronized": self.records_synchronized,
            "errors": self.errors,
            "metadata": self.metadata,
        }