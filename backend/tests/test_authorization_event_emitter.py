from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.role_assignment import RoleAssignment
from app.services.authorization_event_emitter import (
    AuthorizationEventEmitter,
    SYSTEM_AUTHORIZATION_EVENT_ACTOR,
)


def _assignment() -> RoleAssignment:
    assignment = RoleAssignment(
        role_id="role-global-reader",
        subject_type="Account",
        subject_id="account-001",
        assignment_type="Direct",
        status="Active",
        directory_scope="/",
        application_scope=None,
        source_system="Microsoft Entra ID",
        source_identifier="assignment-001",
        confidence_score=100,
    )
    assignment.id = "role-assignment-001"
    assignment.first_seen_at = datetime(
        2026,
        8,
        3,
        8,
        0,
        tzinfo=UTC,
    )
    assignment.last_seen_at = datetime(
        2026,
        8,
        3,
        8,
        0,
        tzinfo=UTC,
    )
    assignment.is_active = True
    return assignment


def _emitter(
    *,
    organization_id: str | None = "organization-027",
):
    db = MagicMock()

    def query(model):
        query_result = MagicMock()

        if model.__name__ == "Account":
            query_result.filter.return_value.one_or_none.return_value = (
                SimpleNamespace(
                    id="account-001",
                    identity_id="identity-001",
                    organizational_identity_id=(
                        "organizational-identity-001"
                    ),
                )
            )
        elif model.__name__ == "Role":
            query_result.filter.return_value.one_or_none.return_value = (
                SimpleNamespace(
                    id="role-global-reader",
                    name="Global Reader",
                    display_name="Global Reader",
                    system_name="Microsoft Entra ID",
                    source_identifier=(
                        "88d8e3e3-8f55-4a1e-953a-9b9898b8876b"
                    ),
                    privilege_level=None,
                )
            )

        return query_result

    db.query.side_effect = query

    event_service = MagicMock()
    event_service.create_pending.side_effect = (
        lambda *, payload, actor: SimpleNamespace(
            payload=payload,
            actor=actor,
        )
    )
    emitter = AuthorizationEventEmitter(
        db,
        organization_id=organization_id,
        event_service=event_service,
    )
    return emitter, event_service


def test_role_assigned_emits_organization_scoped_event():
    emitter, event_service = _emitter()
    assignment = _assignment()
    detected_at = datetime(2026, 8, 3, 10, 0, tzinfo=UTC)

    result = emitter.emit_role_assigned(
        assignment=assignment,
        detected_at=detected_at,
    )

    payload = result.payload

    assert payload.organization_id == "organization-027"
    assert payload.event_type == "ROLE_ASSIGNED"
    assert payload.role_assignment_id == assignment.id
    assert payload.account_id == "account-001"
    assert payload.identity_id == "identity-001"
    assert (
        payload.organizational_identity_id
        == "organizational-identity-001"
    )
    assert payload.current_state_json["role_id"] == (
        "role-global-reader"
    )
    assert payload.is_material is False
    assert payload.risk_level == "Low"
    event_service.create_pending.assert_called_once()
    assert result.actor == SYSTEM_AUTHORIZATION_EVENT_ACTOR


def test_unchanged_role_assignment_emits_nothing():
    emitter, event_service = _emitter()
    assignment = _assignment()

    result = emitter.emit_role_updated_if_changed(
        existing=assignment,
        incoming={
            "assignment_type": "Direct",
            "status": "Active",
            "directory_scope": "/",
            "application_scope": None,
        },
    )

    assert result is None
    event_service.create_pending.assert_not_called()


def test_status_change_emits_role_updated():
    emitter, event_service = _emitter()
    assignment = _assignment()

    result = emitter.emit_role_updated_if_changed(
        existing=assignment,
        incoming={
            "assignment_type": "Direct",
            "status": "Eligible",
            "directory_scope": "/",
            "application_scope": None,
        },
    )

    payload = result.payload

    assert payload.event_type == "ROLE_UPDATED"
    assert payload.previous_status == "Active"
    assert payload.current_status == "Eligible"
    assert payload.evidence_json["changes"]["status"] == {
        "previous": "Active",
        "current": "Eligible",
    }
    event_service.create_pending.assert_called_once()


def test_scope_change_emits_role_updated():
    emitter, _ = _emitter()
    assignment = _assignment()

    result = emitter.emit_role_updated_if_changed(
        existing=assignment,
        incoming={
            "assignment_type": "Direct",
            "status": "Active",
            "directory_scope": "/administrativeUnits/027",
            "application_scope": None,
        },
    )

    assert result.payload.evidence_json["changes"][
        "directory_scope"
    ] == {
        "previous": "/",
        "current": "/administrativeUnits/027",
    }


def test_legacy_reconciliation_without_organization_emits_nothing():
    emitter, event_service = _emitter(organization_id=None)

    result = emitter.emit_role_assigned(
        assignment=_assignment(),
    )

    assert result is None
    event_service.create_pending.assert_not_called()
