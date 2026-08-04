from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.authorization_work_item_generator import (
    AuthorizationWorkItemGenerator,
)


def _event(*, material=True, risk="Critical"):
    return SimpleNamespace(
        id="authorization-event-001",
        organization_id="organization-027",
        identity_id="identity-001",
        event_type="ROLE_ASSIGNED",
        detected_at=datetime(2026, 8, 4, 11, 0, tzinfo=UTC),
        risk_level=risk,
        is_material=material,
        evidence_json={
            "reasons": ["Material privilege assignment."],
            "classification": {
                "capability": "TenantAdministrator",
                "classification_source": (
                    "MicrosoftEntraRolePolicy"
                ),
                "scope_classification": "TenantWide",
                "assignment_classification": "Direct",
                "evidence": {
                    "role_name": "Global Administrator",
                },
            },
        },
        confidence_score=100,
    )


def test_non_material_event_generates_no_work():
    service = MagicMock()
    generator = AuthorizationWorkItemGenerator(
        MagicMock(),
        work_item_service=service,
    )

    assert generator.generate(
        event=_event(material=False, risk="Low")
    ) is None
    service.create_pending.assert_not_called()


def test_material_event_creates_generic_work_item():
    service = MagicMock()
    generator = AuthorizationWorkItemGenerator(
        MagicMock(),
        work_item_service=service,
    )

    generator.generate(event=_event())

    kwargs = service.create_pending.call_args.kwargs
    assert kwargs["source_type"] == "AuthorizationEvent"
    assert kwargs["decision_category"] == "Authorization"
    assert kwargs["title"] == (
        "Review Global Administrator assignment"
    )
    assert kwargs["priority"] == "Critical"
    assert "framework" not in kwargs
