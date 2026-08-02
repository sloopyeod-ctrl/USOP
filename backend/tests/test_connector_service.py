from typing import Any
from unittest import result

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import (
    ConnectorConfiguration,
)
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult
from app.connectors.manager.ConnectorManager import ConnectorManager
from app.services.connector_service import ConnectorService
from app.connectors.provider.ProviderDescriptor import (
    ProviderDescriptor,
)
from app.connectors.provider.ProviderRegistry import (
    ProviderRegistry,
)


class FakeEntraProvider(BaseConnector):
    """
    Deterministic provider used to validate ConnectorService behavior without
    external Microsoft Graph access.
    """

    PROVIDER_NAME = "microsoft-entra"
    DESCRIPTOR = ProviderDescriptor(
        provider_name=PROVIDER_NAME,
        display_name="Microsoft Entra Test Provider",
        vendor="Microsoft",
        component_version="test",
        intelligence_domains=(
            "Identity",
        ),
        capabilities=(
            "identities",
        ),
        supported_modes=(
            "test",
        ),
    )

    def __init__(self):
        super().__init__(
            ConnectorConfiguration(
                provider_name=self.PROVIDER_NAME,
                environment="test",
                settings={
                    "mode": "test",
                },
            )
        )

    def authenticate(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="authenticate",
            success=True,
            message="Test authentication ready.",
        ).complete()

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            provider_name=self.provider_name,
            healthy=True,
            status="healthy",
            details={
                "mode": "test",
            },
        )

    def collect(self) -> dict[str, Any]:
        return {
            "identities": [
                {
                    "source_identifier": "test-identity-001",
                }
            ],
            "accounts": [],
            "groups": [],
            "roles": [],
            "memberships": [],
            "role_assignments": [],
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
            message="Test synchronization completed.",
            records_collected=1,
            metadata={
                "mode": "test",
            },
        ).complete()


def build_service() -> ConnectorService:
    manager = ConnectorManager()
    registry = ProviderRegistry()

    registry.register(
        descriptor=FakeEntraProvider.DESCRIPTOR,
        factory=FakeEntraProvider,
    )

    return ConnectorService(
        manager=manager,
        registry=registry,
        register_default_providers=False,
    )


def test_list_connectors_returns_canonical_provider_names():
    service = build_service()

    assert service.list_connectors() == [
        "microsoft-entra",
    ]


def test_collect_accepts_canonical_provider_name():
    service = build_service()

    result = service.collect(
        "microsoft-entra"
    )

    assert result is not None
    assert len(result["identities"]) == 1


def test_collect_accepts_temporary_entra_alias():
    service = build_service()

    result = service.collect(
        "entra"
    )

    assert result is not None
    assert len(result["identities"]) == 1


def test_health_returns_serialized_provider_health():
    service = build_service()

    result = service.health()

    assert len(result) == 1
    assert result[0]["provider_name"] == "microsoft-entra"
    assert result[0]["healthy"] is True
    assert result[0]["status"] == "healthy"
    assert result[0]["checked_at"] is not None
    assert result[0]["details"]["mode"] == "test"


def test_synchronize_returns_serialized_connector_result():
    service = build_service()

    result = service.synchronize(
        "microsoft-entra"
    )

    assert result is not None
    assert result["provider_name"] == "microsoft-entra"
    assert result["operation"] == "synchronize"
    assert result["success"] is True
    assert result["records_collected"] == 1
    assert result["metadata"]["mode"] == "test"


def test_synchronize_accepts_temporary_entra_alias():
    service = build_service()

    result = service.synchronize(
        "entra"
    )

    assert result is not None
    assert result["provider_name"] == "microsoft-entra"
    assert result["success"] is True

def test_unknown_provider_preserves_none_contract():
    service = build_service()

    assert service.collect("unknown-provider") is None
    assert service.synchronize("unknown-provider") is None

def test_service_activates_registry_providers():
    service = build_service()

    assert service.manager.get(
        "microsoft-entra"
    ) is not None


def test_service_lists_provider_descriptors():
    service = build_service()

    result = service.list_provider_descriptors()

    assert result == [
        {
            "provider_name": "microsoft-entra",
            "display_name": (
                "Microsoft Entra Test Provider"
            ),
            "vendor": "Microsoft",
            "component_version": "test",
            "intelligence_domains": [
                "Identity",
            ],
            "capabilities": [
                "identities",
            ],
            "supported_modes": [
                "test",
            ],
        }
    ]    
