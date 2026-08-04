from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.pending_decision_resolution_service import (
    PendingDecisionResolutionConflictError,
    PendingDecisionResolutionNotFoundError,
    PendingDecisionResolutionService,
)


def _service(work_item):
    db = MagicMock()

    decision_service = MagicMock()
    decision_service.create_decision_record_pending.return_value = (
        SimpleNamespace(id="decision-001")
    )

    work_item_service = MagicMock()
    work_item_service.get_by_id.return_value = work_item
    work_item_service.resolve_pending.return_value = (
        SimpleNamespace(id="work-item-001")
    )

    return (
        PendingDecisionResolutionService(
            db,
            decision_service=decision_service,
            work_item_service=work_item_service,
        ),
        db,
        decision_service,
        work_item_service,
    )


def test_resolution_commits_once():
    work_item = SimpleNamespace(
        id="work-item-001",
        identity_id="identity-001",
        status="Pending",
    )
    service, db, decision_service, work_item_service = (
        _service(work_item)
    )

    record = service.resolve_with_decision(
        organization_id="organization-027",
        work_item_id="work-item-001",
        recommendation_id="recommendation-001",
        action=SimpleNamespace(
            actor="analyst@example.com"
        ),
    )

    assert record.id == "decision-001"
    decision_service.create_decision_record_pending.assert_called_once()
    work_item_service.resolve_pending.assert_called_once()
    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()


def test_missing_work_item_rolls_back():
    service, db, _, _ = _service(None)

    with pytest.raises(
        PendingDecisionResolutionNotFoundError
    ):
        service.resolve_with_decision(
            organization_id="organization-027",
            work_item_id="missing",
            recommendation_id="recommendation-001",
            action=SimpleNamespace(actor=None),
        )

    db.rollback.assert_called_once_with()


def test_resolved_work_item_is_conflict():
    work_item = SimpleNamespace(
        id="work-item-001",
        identity_id="identity-001",
        status="Resolved",
    )
    service, db, _, _ = _service(work_item)

    with pytest.raises(
        PendingDecisionResolutionConflictError
    ):
        service.resolve_with_decision(
            organization_id="organization-027",
            work_item_id="work-item-001",
            recommendation_id="recommendation-001",
            action=SimpleNamespace(actor=None),
        )

    db.rollback.assert_called_once_with()
