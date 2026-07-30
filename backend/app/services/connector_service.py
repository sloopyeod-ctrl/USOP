from typing import Any

from app.connectors.manager.ConnectorManager import ConnectorManager
from app.connectors.microsoft.EntraProvider import EntraProvider


class ConnectorService:
    """
    Application façade for connector-provider operations.

    ConnectorManager is the authority for provider registration and lifecycle
    orchestration. ConnectorService adapts provider-domain results into
    API-compatible dictionaries.

    The legacy "entra" identifier remains a temporary compatibility alias for
    the canonical "microsoft-entra" provider identifier.
    """

    PROVIDER_ALIASES = {
        "entra": EntraProvider.PROVIDER_NAME,
    }

    def __init__(
        self,
        manager: ConnectorManager | None = None,
        *,
        register_default_providers: bool = True,
    ):
        self.manager = manager or ConnectorManager()

        if register_default_providers:
            self._register_default_providers()

    def _register_default_providers(self) -> None:
        """
        Register built-in providers without replacing injected providers.
        """

        provider_name = EntraProvider.PROVIDER_NAME

        if self.manager.get(provider_name) is None:
            self.manager.register(
                EntraProvider()
            )

    @classmethod
    def _resolve_provider_name(
        cls,
        provider_name: str,
    ) -> str:
        """
        Resolve temporary compatibility aliases to canonical provider names.
        """

        normalized_name = str(
            provider_name or ""
        ).strip().lower()

        return cls.PROVIDER_ALIASES.get(
            normalized_name,
            normalized_name,
        )

    def list_connectors(self) -> list[str]:
        """
        Return canonical registered provider identifiers.
        """

        return list(
            self.manager.providers()
        )

    def health(self) -> list[dict[str, Any]]:
        """
        Return serialized health results for all registered providers.
        """

        return [
            result.to_dict()
            for result in self.manager.health()
        ]

    def collect(
        self,
        connector_name: str,
    ) -> dict[str, Any] | None:
        """
        Collect provider records without persistence.

        Unknown providers preserve the existing None response contract.
        """

        provider_name = self._resolve_provider_name(
            connector_name
        )

        provider = self.manager.get(
            provider_name
        )

        if provider is None:
            return None

        return provider.collect()

    def synchronize(
        self,
        connector_name: str,
    ) -> dict[str, Any] | None:
        """
        Execute provider-level synchronization and serialize its result.

        This operation performs the provider collection lifecycle. Canonical
        persistence remains owned by SynchronizationEngine.

        Unknown providers preserve the existing None response contract.
        """

        provider_name = self._resolve_provider_name(
            connector_name
        )

        if self.manager.get(provider_name) is None:
            return None

        result = self.manager.synchronize(
            provider_name
        )

        return result.to_dict()