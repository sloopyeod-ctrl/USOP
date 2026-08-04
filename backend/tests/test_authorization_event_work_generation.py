from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.authorization_event_emitter import (
    AuthorizationEventEmitter,
)


def test_emitter_passes_staged_event_to_work_generator():
    emitter = object.__new__(AuthorizationEventEmitter)
    emitter.organization_id = "organization-027"
    emitter.db = MagicMock()
    emitter.event_service = MagicMock()
    emitter.classification_service = MagicMock()
    emitter.materiality_service = MagicMock()
    emitter.work_item_generator = MagicMock()

    event = SimpleNamespace(id="authorization-event-001")
    emitter.event_service.create_pending.return_value = event
    emitter._account_context = MagicMock(
        return_value=(None, None, None)
    )
    emitter._classify_event = MagicMock(
        return_value={
            "risk_level": "Critical",
            "is_material": True,
            "reasons": [],
            "classification": {},
        }
    )

    assignment = SimpleNamespace(
        id="assignment-001",
        subject_type="Account",
        subject_id="account-001",
        source_system="Microsoft Entra ID",
        source_identifier="provider-assignment-001",
        confidence_score=100,
    )

    result = emitter._emit(
        event_type="ROLE_ASSIGNED",
        assignment=assignment,
        previous_state=None,
        current_state={
            "assignment_type": "Direct",
            "status": "Active",
            "directory_scope": "/",
            "application_scope": None,
            "first_seen_at": None,
        },
        evidence_json={"change_kind": "created"},
    )

    assert result is event
    emitter.work_item_generator.generate.assert_called_once_with(
        event=event
    )
