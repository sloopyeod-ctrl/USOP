from __future__ import annotations

from collections.abc import Callable, Iterable

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.provider.ProviderDescriptor import (
    ProviderDescriptor,
)


ProviderFactory = Callable[[], BaseConnector]


class ProviderRegistry:
    """
    Catalog of connector-provider descriptors and factories.

    The registry owns provider discovery metadata.

    It does not own:

    - provider runtime lifecycle
    - synchronization
    - health evaluation
    - customer configuration
    - credentials
    - licensing

    ConnectorManager remains responsible for active provider instances.
    """

    def __init__(self) -> None:
        self._descriptors: dict[
            str,
            ProviderDescriptor,
        ] = {}

        self._factories: dict[
            str,
            ProviderFactory,
        ] = {}

    def register(
        self,
        descriptor: ProviderDescriptor,
        factory: ProviderFactory,
    ) -> None:
        provider_name = descriptor.provider_name

        if provider_name in self._descriptors:
            raise ValueError(
                f"Provider already registered: {provider_name}"
            )

        self._descriptors[
            provider_name
        ] = descriptor

        self._factories[
            provider_name
        ] = factory

    def unregister(
        self,
        provider_name: str,
    ) -> None:
        normalized_name = self._normalize_provider_name(
            provider_name
        )

        self._descriptors.pop(
            normalized_name,
            None,
        )

        self._factories.pop(
            normalized_name,
            None,
        )

    def get_descriptor(
        self,
        provider_name: str,
    ) -> ProviderDescriptor | None:
        normalized_name = self._normalize_provider_name(
            provider_name
        )

        return self._descriptors.get(
            normalized_name
        )

    def descriptors(
        self,
    ) -> Iterable[ProviderDescriptor]:
        return tuple(
            self._descriptors[
                provider_name
            ]
            for provider_name in sorted(
                self._descriptors
            )
        )

    def provider_names(
        self,
    ) -> Iterable[str]:
        return tuple(
            sorted(
                self._descriptors
            )
        )

    def create(
        self,
        provider_name: str,
    ) -> BaseConnector | None:
        normalized_name = self._normalize_provider_name(
            provider_name
        )

        factory = self._factories.get(
            normalized_name
        )

        if factory is None:
            return None

        provider = factory()

        if (
            provider.provider_name
            != normalized_name
        ):
            raise ValueError(
                "Provider factory returned a provider whose "
                "name does not match its descriptor."
            )

        return provider

    def create_all(
        self,
    ) -> list[BaseConnector]:
        providers: list[BaseConnector] = []

        for provider_name in self.provider_names():
            provider = self.create(
                provider_name
            )

            if provider is not None:
                providers.append(
                    provider
                )

        return providers

    @staticmethod
    def _normalize_provider_name(
        provider_name: str,
    ) -> str:
        return str(
            provider_name or ""
        ).strip().lower()