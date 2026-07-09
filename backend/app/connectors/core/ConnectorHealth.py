from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ConnectorHealth:
    """
    Represents the current health state of a connector provider.
    """

    provider_name: str
    healthy: bool
    status: str
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "healthy": self.healthy,
            "status": self.status,
            "checked_at": self.checked_at.isoformat(),
            "details": self.details,
        }