from types import SimpleNamespace
from unittest.mock import MagicMock

from app.repositories.pending_decision_work_item_repository import (
    PendingDecisionWorkItemRepository,
)


def test_create_pending_adds_and_flushes():
    db = MagicMock()
    repository = PendingDecisionWorkItemRepository(db)
    work_item = SimpleNamespace(id="work-item-001")

    result = repository.create_pending(work_item)

    assert result is work_item
    db.add.assert_called_once_with(work_item)
    db.flush.assert_called_once_with()


def test_source_lookup_is_organization_scoped():
    db = MagicMock()
    filtered = db.query.return_value.filter.return_value
    expected = SimpleNamespace(id="work-item-001")
    filtered.one_or_none.return_value = expected

    result = (
        PendingDecisionWorkItemRepository(db)
        .get_by_source_for_organization(
            organization_id="organization-027",
            source_type="AuthorizationEvent",
            source_id="event-001",
        )
    )

    assert result is expected
    filtered.one_or_none.assert_called_once_with()
