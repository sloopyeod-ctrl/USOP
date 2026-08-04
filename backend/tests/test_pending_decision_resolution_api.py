from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1.pending_decision_resolution import (
    resolve_pending_decision_with_record,
)
from app.services.pending_decision_resolution_service import (
    PendingDecisionResolutionConflictError,
)


def test_resolution_endpoint_returns_record(monkeypatch):
    service = MagicMock()
    service.resolve_with_decision.return_value = (
        SimpleNamespace(id="decision-001")
    )

    monkeypatch.setattr(
        "app.api.v1.pending_decision_resolution."
        "PendingDecisionResolutionService",
        lambda db: service,
    )

    result = resolve_pending_decision_with_record(
        organization_id="organization-027",
        work_item_id="work-item-001",
        recommendation_id="recommendation-001",
        action=SimpleNamespace(actor=None),
        db=MagicMock(),
    )

    assert result.id == "decision-001"


def test_resolution_conflict_becomes_409(monkeypatch):
    service = MagicMock()
    service.resolve_with_decision.side_effect = (
        PendingDecisionResolutionConflictError(
            "Already resolved."
        )
    )

    monkeypatch.setattr(
        "app.api.v1.pending_decision_resolution."
        "PendingDecisionResolutionService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as error:
        resolve_pending_decision_with_record(
            organization_id="organization-027",
            work_item_id="work-item-001",
            recommendation_id="recommendation-001",
            action=SimpleNamespace(actor=None),
            db=MagicMock(),
        )

    assert error.value.status_code == 409
