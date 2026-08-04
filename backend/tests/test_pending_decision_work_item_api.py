from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1.pending_decision_work_items import (
    list_pending_decision_work_items,
)
from app.services.pending_decision_work_item_service import (
    PendingDecisionWorkItemOrganizationNotFoundError,
    PendingDecisionWorkItemValidationError,
)


def test_list_endpoint_passes_organization_and_status(monkeypatch):
    service = MagicMock()
    service.list_for_organization.return_value = [
        SimpleNamespace(id="work-item-001")
    ]

    monkeypatch.setattr(
        "app.api.v1.pending_decision_work_items."
        "PendingDecisionWorkItemService",
        lambda db: service,
    )

    db = MagicMock()
    result = list_pending_decision_work_items(
        organization_id="organization-027",
        work_status="Pending",
        db=db,
    )

    assert len(result) == 1
    service.list_for_organization.assert_called_once_with(
        organization_id="organization-027",
        status="Pending",
    )


def test_unknown_organization_becomes_404(monkeypatch):
    service = MagicMock()
    service.list_for_organization.side_effect = (
        PendingDecisionWorkItemOrganizationNotFoundError(
            "Unknown Organization."
        )
    )

    monkeypatch.setattr(
        "app.api.v1.pending_decision_work_items."
        "PendingDecisionWorkItemService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as error:
        list_pending_decision_work_items(
            organization_id="missing",
            work_status=None,
            db=MagicMock(),
        )

    assert error.value.status_code == 404


def test_invalid_status_becomes_400(monkeypatch):
    service = MagicMock()
    service.list_for_organization.side_effect = (
        PendingDecisionWorkItemValidationError(
            "Unknown work-item status."
        )
    )

    monkeypatch.setattr(
        "app.api.v1.pending_decision_work_items."
        "PendingDecisionWorkItemService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as error:
        list_pending_decision_work_items(
            organization_id="organization-027",
            work_status="Invalid",
            db=MagicMock(),
        )

    assert error.value.status_code == 400
