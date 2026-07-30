from typing import Any

from app.connectors.manager.ConnectorManager import (
    ConnectorManager,
)
from app.connectors.microsoft.EntraProvider import (
    EntraProvider,
)
from app.connectors.provider.ProviderRegistry import (
    ProviderRegistry,
)


class ConnectorService:
    """
    Application facade for connector-provider operations.

    ProviderRegistry owns provider discovery metadata and construction.

    ConnectorManager owns active provider instances and runtime lifecycle
    orchestration.

    ConnectorService adapts those capabilities into application-facing
    operations.

    The legacy "entra" identifier remains a temporary compatibility alias for
    the canonical "microsoft-entra" provider identifier.
    """

    PROVIDER_ALIASES = {
        "entra": EntraProvider.PROVIDER_NAME,
    }

    def __init__(
        self,
        manager: ConnectorManager | None = None,
        registry: ProviderRegistry | None = None,
        *,
        register_default_providers: bool = True,
    ):
        self.manager = manager or ConnectorManager()
        self.registry = registry or ProviderRegistry()

        if register_default_providers:
            self._register_default_providers()

        self._activate_registered_providers()

    def _register_default_providers(self) -> None:
        """
        Register built-in provider descriptors and factories.
        """

        provider_name = (
            EntraProvider.DESCRIPTOR.provider_name
        )

        if (
            self.registry.get_descriptor(
                provider_name
            )
            is None
        ):
            self.registry.register(
                descriptor=EntraProvider.DESCRIPTOR,
                factory=EntraProvider,
            )

    def _activate_registered_providers(
        self,
    ) -> None:
        """
        Construct registered providers and add them to ConnectorManager.

        Existing injected manager providers are preserved.
        """

        for provider_name in (
            self.registry.provider_names()
        ):
            if self.manager.get(provider_name) is not None:
                continue

            provider = self.registry.create(
                provider_name
            )

            if provider is not None:
                self.manager.register(
                    provider
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

    def list_connectors(
        self,
    ) -> list[str]:
        """
        Return canonical active provider identifiers.
        """

        return list(
            self.manager.providers()
        )

    def list_provider_descriptors(
        self,
    ) -> list[dict[str, object]]:
        """
        Return immutable metadata for registered provider types.
        """

        return [
            descriptor.to_dict()
            for descriptor in self.registry.descriptors()
        ]

    def health(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return serialized health results for active providers.
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

        Canonical persistence remains owned by SynchronizationEngine.
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