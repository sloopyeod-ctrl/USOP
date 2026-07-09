from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectorConfiguration:
    """
    Configuration contract for connector providers.
    """

    provider_name: str
    enabled: bool = True
    environment: str = "development"
    settings: dict[str, Any] = field(default_factory=dict)
    secrets_reference: str | None = None

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "enabled": self.enabled,
            "environment": self.environment,
            "settings": self.settings,
            "secrets_reference": self.secrets_reference,
        }