from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.authorization_event import AuthorizationEvent
from app.repositories.authorization_event_repository import (
    AuthorizationEventRepository,
)


def test_create_pending_adds_and_flushes():
    db = MagicMock()
    repository = AuthorizationEventRepository(db)
    event = AuthorizationEvent(
        organization_id="organization-027",
        subject_type="Account",
        subject_id="account-001",
        event_type="ROLE_ASSIGNED",
        detected_at=datetime.now(UTC),
    )

    result = repository.create_pending(event)

    assert result is event
    db.add.assert_called_once_with(event)
    db.flush.assert_called_once_with()


def test_scoped_get_uses_one_or_none():
    db = MagicMock()
    query = db.query.return_value
    filtered = query.filter.return_value
    expected = SimpleNamespace(id="event-001")
    filtered.one_or_none.return_value = expected

    repository = AuthorizationEventRepository(db)

    result = repository.get_by_id_for_organization(
        organization_id="organization-027",
        event_id="event-001",
    )

    assert result is expected
    filtered.one_or_none.assert_called_once_with()
