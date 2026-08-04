from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.pending_decision_work_item_service import (
    PendingDecisionWorkItemOrganizationNotFoundError,
    PendingDecisionWorkItemService,
    PendingDecisionWorkItemValidationError,
)


def _service(*, existing=None):
    db = MagicMock()
    repository = MagicMock()
    repository.get_by_source_for_organization.return_value = (
        existing
    )
    repository.create_pending.side_effect = lambda item: item

    organization_repository = MagicMock()
    organization_repository.get_by_id.return_value = (
        SimpleNamespace(id="organization-027")
    )

    audit_service = MagicMock()

    return (
        PendingDecisionWorkItemService(
            db,
            repository=repository,
            organization_repository=organization_repository,
            audit_service=audit_service,
        ),
        db,
        repository,
        audit_service,
    )


def _kwargs():
    return {
        "organization_id": " organization-027 ",
        "identity_id": " identity-001 ",
        "source_type": " AuthorizationEvent ",
        "source_id": " event-001 ",
        "decision_category": " Authorization ",
        "title": " Review privileged role assignment ",
        "priority": " Critical ",
        "risk_level": " Critical ",
        "materiality_reason": " Material privilege change ",
        "evidence_snapshot_json": {
            "event_type": "ROLE_ASSIGNED",
        },
        "actor": "system:authorization",
    }


def test_create_pending_normalizes_and_stages_audit():
    service, db, repository, audit_service = _service()

    work_item = service.create_pending(**_kwargs())

    assert work_item.organization_id == "organization-027"
    assert work_item.identity_id == "identity-001"
    assert work_item.source_type == "AuthorizationEvent"
    assert work_item.source_id == "event-001"
    assert work_item.decision_category == "Authorization"
    assert work_item.priority == "Critical"
    assert work_item.status == "Pending"
    assert work_item.created_by == "system:authorization"
    repository.create_pending.assert_called_once_with(work_item)
    audit_service.record_pending.assert_called_once()
    db.commit.assert_not_called()


def test_duplicate_source_returns_existing_item():
    existing = SimpleNamespace(id="existing-work-item")
    service, _, repository, audit_service = _service(
        existing=existing
    )

    result = service.create_pending(**_kwargs())

    assert result is existing
    repository.create_pending.assert_not_called()
    audit_service.record_pending.assert_not_called()


def test_unknown_organization_is_rejected():
    service, _, _, _ = _service()
    service.organization_repository.get_by_id.return_value = None

    with pytest.raises(
        PendingDecisionWorkItemOrganizationNotFoundError
    ):
        service.create_pending(**_kwargs())


def test_non_object_evidence_is_rejected():
    service, _, _, _ = _service()
    kwargs = _kwargs()
    kwargs["evidence_snapshot_json"] = []

    with pytest.raises(
        PendingDecisionWorkItemValidationError
    ):
        service.create_pending(**kwargs)


def test_create_commits_and_refreshes():
    service, db, _, _ = _service()

    work_item = service.create(**_kwargs())

    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(work_item)
