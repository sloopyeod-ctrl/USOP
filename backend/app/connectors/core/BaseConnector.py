from abc import ABC, abstractmethod
from typing import Any

from app.connectors.core.ConnectorConfiguration import ConnectorConfiguration
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult


class BaseConnector(ABC):
    """
    Base contract for all USOP connector providers.

    Connectors are vendor-specific providers that collect external security data,
    normalize it into USOP-compatible structures, and return standardized results.

    Implementations should not write directly to visualization layers.
    """

    def __init__(self, configuration: ConnectorConfiguration):
        self.configuration = configuration
        self.provider_name = configuration.provider_name

    def initialize(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="initialize",
            success=True,
            message=f"{self.provider_name} initialized.",
        ).complete()

    @abstractmethod
    def authenticate(self) -> ConnectorResult:
        """
        Authenticate to the external provider.
        """
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ConnectorHealth:
        """
        Return provider health.
        """
        raise NotImplementedError

    @abstractmethod
    def collect(self) -> dict[str, Any]:
        """
        Collect raw provider data.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize raw provider data into USOP-compatible structures.
        """
        raise NotImplementedError

    @abstractmethod
    def synchronize(self) -> ConnectorResult:
        """
        Execute the full provider synchronization lifecycle.
        """
        raise NotImplementedError
    