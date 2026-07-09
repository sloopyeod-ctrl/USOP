from __future__ import annotations

from typing import Dict, Iterable

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult


class ConnectorManager:
    """
    Coordinates connector providers.

    The manager is intentionally vendor agnostic.

    Providers register themselves with the manager.

    The manager owns lifecycle orchestration.

    It never owns provider-specific logic.
    """

    def __init__(self):
        self._providers: Dict[str, BaseConnector] = {}

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register(self, provider: BaseConnector) -> None:
        self._providers[provider.provider_name] = provider

    def unregister(self, provider_name: str) -> None:
        self._providers.pop(provider_name, None)

    def get(self, provider_name: str) -> BaseConnector | None:
        return self._providers.get(provider_name)

    def providers(self) -> Iterable[str]:
        return sorted(self._providers.keys())

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def initialize_all(self) -> list[ConnectorResult]:
        results = []

        for provider in self._providers.values():
            results.append(provider.initialize())

        return results

    def health(self) -> list[ConnectorHealth]:
        return [
            provider.health()
            for provider in self._providers.values()
        ]

    def synchronize(self, provider_name: str) -> ConnectorResult:
        provider = self.get(provider_name)

        if provider is None:
            result = ConnectorResult(
                provider_name=provider_name,
                operation="synchronize",
                success=False,
                message="Provider not registered.",
            )
            return result.complete()

        return provider.synchronize()

    def synchronize_all(self) -> list[ConnectorResult]:
        return [
            provider.synchronize()
            for provider in self._providers.values()
        ]