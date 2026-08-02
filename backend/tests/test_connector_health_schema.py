from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.connector_health import ConnectorHealthRead


def build_payload() -> dict[str, object]:
    return {
        "provider_name": "microsoft-entra",
        "healthy": True,
        "status": "healthy",
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "details": {
            "mode": "live",
            "live_capabilities": [
                "accounts",
                "groups",
                "identities",
                "memberships",
                "role_assignments",
                "roles",
            ],
        },
    }


def test_connector_health_read_accepts_complete_contract():
    health = ConnectorHealthRead(
        **build_payload()
    )

    assert health.provider_name == "microsoft-entra"
    assert health.healthy is True
    assert health.status == "healthy"
    assert health.checked_at.tzinfo is not None
    assert health.details["mode"] == "live"


@pytest.mark.parametrize(
    "field_name",
    [
        "provider_name",
        "healthy",
        "status",
        "checked_at",
        "details",
    ],
)
def test_connector_health_read_requires_every_field(
    field_name: str,
):
    payload = build_payload()
    payload.pop(field_name)

    with pytest.raises(ValidationError):
        ConnectorHealthRead(
            **payload
        )


def test_connector_health_read_rejects_unknown_fields():
    payload = build_payload()
    payload["last_synchronized_at"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    with pytest.raises(ValidationError):
        ConnectorHealthRead(
            **payload
        )


def test_connector_health_read_allows_provider_specific_details():
    payload = build_payload()

    payload["details"] = {
        "mode": "live",
        "tenant": "example-tenant",
        "latency_ms": 42,
        "authenticated": True,
    }

    health = ConnectorHealthRead(
        **payload
    )

    assert health.details == payload["details"]