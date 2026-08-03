from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.schemas.authorization_event import AuthorizationEventCreate
from app.services.authorization_event_service import (
    AuthorizationEventService,
)


def _payload() -> AuthorizationEventCreate:
    return AuthorizationEventCreate(
        organization_id=" organization-027 ",
        organizational_identity_id="organizational-identity-001",
        identity_id="identity-001",
        account_id="account-001",
        role_assignment_id="assignment-001",
        subject_type=" Account ",
        subject_id=" account-001 ",
        event_type=" PIM_ACTIVATED ",
        assignment_type="Eligible",
        previous_status="Eligible",
        current_status="Active",
        effective_start=datetime(2026, 8, 3, 8, 0, tzinfo=UTC),
        effective_end=datetime(2026, 8, 3, 16, 0, tzinfo=UTC),
        detected_at=datetime(2026, 8, 3, 8, 1, tzinfo=UTC),
        risk_level=" Critical ",
        is_material=True,
        source_system="Microsoft Entra ID",
    )


def test_create_pending_normalizes_and_stages_event():
    db = MagicMock()
    repository = MagicMock()
    organization_repository = MagicMock()
    organization_repository.get_by_id.return_value = SimpleNamespace(
        id="organization-027"
    )
    repository.create_pending.side_effect = lambda event: event

    service = AuthorizationEventService(
        db,
        repository=repository,
        organization_repository=organization_repository,
    )

    event = service.create_pending(
        payload=_payload(),
        actor=" analyst@example.com ",
    )

    assert event.organization_id == "organization-027"
    assert event.subject_type == "Account"
    assert event.subject_id == "account-001"
    assert event.event_type == "PIM_ACTIVATED"
    assert event.risk_level == "Critical"
    assert event.created_by == "analyst@example.com"
    assert event.updated_by == "analyst@example.com"
    repository.create_pending.assert_called_once_with(event)
    db.commit.assert_not_called()


def test_create_commits_and_refreshes():
    db = MagicMock()
    repository = MagicMock()
    organization_repository = MagicMock()
    organization_repository.get_by_id.return_value = SimpleNamespace(
        id="organization-027"
    )
    repository.create_pending.side_effect = lambda event: event

    service = AuthorizationEventService(
        db,
        repository=repository,
        organization_repository=organization_repository,
    )

    event = service.create(
        payload=_payload(),
        actor="analyst@example.com",
    )

    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(event)


def test_unknown_organization_is_rejected():
    db = MagicMock()
    repository = MagicMock()
    organization_repository = MagicMock()
    organization_repository.get_by_id.return_value = None

    service = AuthorizationEventService(
        db,
        repository=repository,
        organization_repository=organization_repository,
    )

    with pytest.raises(
        ValueError,
        match="unknown Organization",
    ):
        service.create_pending(
            payload=_payload(),
            actor="analyst@example.com",
        )


def test_blank_actor_is_rejected():
    organization_repository = MagicMock()
    organization_repository.get_by_id.return_value = SimpleNamespace(
        id="organization-027"
    )

    service = AuthorizationEventService(
        MagicMock(),
        repository=MagicMock(),
        organization_repository=organization_repository,
    )

    with pytest.raises(ValueError, match="actor cannot be blank"):
        service.create_pending(
            payload=_payload(),
            actor="   ",
        )


def test_service_exposes_no_update_or_delete_workflow():
    service = AuthorizationEventService(MagicMock())

    assert not hasattr(service, "update")
    assert not hasattr(service, "delete")
