import pytest
from pydantic import ValidationError

from app.schemas.provider import ProviderDescriptorRead


def build_payload() -> dict[str, object]:
    return {
        "provider_name": "microsoft-entra",
        "display_name": "Microsoft Entra ID",
        "vendor": "Microsoft",
        "component_version": "1.0.0",
        "intelligence_domains": [
            "Authentication",
            "Authorization",
            "Identity",
        ],
        "capabilities": [
            "accounts",
            "groups",
            "identities",
            "memberships",
            "role_assignments",
            "roles",
        ],
        "supported_modes": [
            "demo",
            "live",
        ],
    }


def test_provider_descriptor_read_accepts_complete_contract():
    provider = ProviderDescriptorRead(
        **build_payload()
    )

    assert provider.provider_name == "microsoft-entra"
    assert provider.display_name == "Microsoft Entra ID"
    assert provider.vendor == "Microsoft"
    assert provider.component_version == "1.0.0"

    assert provider.intelligence_domains == [
        "Authentication",
        "Authorization",
        "Identity",
    ]

    assert provider.capabilities == [
        "accounts",
        "groups",
        "identities",
        "memberships",
        "role_assignments",
        "roles",
    ]

    assert provider.supported_modes == [
        "demo",
        "live",
    ]


@pytest.mark.parametrize(
    "field_name",
    [
        "provider_name",
        "display_name",
        "vendor",
        "component_version",
        "intelligence_domains",
        "capabilities",
        "supported_modes",
    ],
)
def test_provider_descriptor_read_requires_every_field(
    field_name: str,
):
    payload = build_payload()
    payload.pop(field_name)

    with pytest.raises(ValidationError):
        ProviderDescriptorRead(
            **payload
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "intelligence_domains",
        "capabilities",
        "supported_modes",
    ],
)
def test_provider_descriptor_read_rejects_empty_collections(
    field_name: str,
):
    payload = build_payload()
    payload[field_name] = []

    with pytest.raises(ValidationError):
        ProviderDescriptorRead(
            **payload
        )


def test_provider_descriptor_read_rejects_unknown_fields():
    payload = build_payload()
    payload["healthy"] = True

    with pytest.raises(ValidationError):
        ProviderDescriptorRead(
            **payload
        )
