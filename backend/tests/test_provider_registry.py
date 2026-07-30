from typing import Any

import pytest

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import (
    ConnectorConfiguration,
)
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult
from app.connectors.provider.ProviderDescriptor import (
    ProviderDescriptor,
)
from app.connectors.provider.ProviderRegistry import (
    ProviderRegistry,
)


class FakeProvider(BaseConnector):
    PROVIDER_NAME = "example-provider"

    def __init__(self):
        super().__init__(
            ConnectorConfiguration(
                provider_name=self.PROVIDER_NAME,
                environment="test",
            )
        )

    def authenticate(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="authenticate",
            success=True,
            message="Ready.",
        ).complete()

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            provider_name=self.provider_name,
            healthy=True,
            status="healthy",
        )

    def collect(self) -> dict[str, Any]:
        return {
            "objects": [],
        }

    def normalize(
        self,
        raw_data: dict[str, Any],
    ) -> dict[str, Any]:
        return raw_data

    def synchronize(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="synchronize",
            success=True,
            message="Complete.",
        ).complete()


def build_descriptor() -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_name="example-provider",
        display_name="Example Provider",
        vendor="Example",
        component_version="1.0.0",
        intelligence_domains=(
            "Identity",
            "Infrastructure",
        ),
        capabilities=(
            "accounts",
            "devices",
        ),
        supported_modes=(
            "demo",
            "live",
        ),
    )


def test_descriptor_normalizes_collection_order():
    descriptor = ProviderDescriptor(
        provider_name="example-provider",
        display_name="Example Provider",
        vendor="Example",
        component_version="1.0.0",
        intelligence_domains=(
            "Infrastructure",
            "Identity",
            "Identity",
        ),
        capabilities=(
            "devices",
            "accounts",
            "devices",
        ),
        supported_modes=(
            "live",
            "demo",
        ),
    )

    assert descriptor.intelligence_domains == (
        "Identity",
        "Infrastructure",
    )

    assert descriptor.capabilities == (
        "accounts",
        "devices",
    )

    assert descriptor.supported_modes == (
        "demo",
        "live",
    )


def test_descriptor_exposes_capability_queries():
    descriptor = build_descriptor()

    assert descriptor.supports_domain(
        "Identity"
    ) is True

    assert descriptor.supports_capability(
        "devices"
    ) is True

    assert descriptor.supports_mode(
        "live"
    ) is True

    assert descriptor.supports_capability(
        "roles"
    ) is False


def test_descriptor_rejects_noncanonical_provider_name():
    with pytest.raises(
        ValueError,
        match="canonical lowercase",
    ):
        ProviderDescriptor(
            provider_name="Example-Provider",
            display_name="Example Provider",
            vendor="Example",
            component_version="1.0.0",
            intelligence_domains=("Identity",),
            capabilities=("accounts",),
            supported_modes=("demo",),
        )


def test_registry_registers_descriptor_and_factory():
    registry = ProviderRegistry()
    descriptor = build_descriptor()

    registry.register(
        descriptor=descriptor,
        factory=FakeProvider,
    )

    assert list(
        registry.provider_names()
    ) == [
        "example-provider",
    ]

    assert (
        registry.get_descriptor(
            "example-provider"
        )
        == descriptor
    )


def test_registry_creates_registered_provider():
    registry = ProviderRegistry()

    registry.register(
        descriptor=build_descriptor(),
        factory=FakeProvider,
    )

    provider = registry.create(
        "example-provider"
    )

    assert provider is not None
    assert provider.provider_name == "example-provider"


def test_registry_rejects_duplicate_provider():
    registry = ProviderRegistry()
    descriptor = build_descriptor()

    registry.register(
        descriptor=descriptor,
        factory=FakeProvider,
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            descriptor=descriptor,
            factory=FakeProvider,
        )


def test_registry_rejects_factory_name_mismatch():
    class MismatchedProvider(FakeProvider):
        PROVIDER_NAME = "different-provider"

        def __init__(self):
            BaseConnector.__init__(
                self,
                ConnectorConfiguration(
                    provider_name=self.PROVIDER_NAME,
                    environment="test",
                ),
            )

    registry = ProviderRegistry()

    registry.register(
        descriptor=build_descriptor(),
        factory=MismatchedProvider,
    )

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        registry.create(
            "example-provider"
        )


def test_registry_unknown_provider_returns_none():
    registry = ProviderRegistry()

    assert registry.create(
        "unknown-provider"
    ) is None

    assert registry.get_descriptor(
        "unknown-provider"
    ) is None