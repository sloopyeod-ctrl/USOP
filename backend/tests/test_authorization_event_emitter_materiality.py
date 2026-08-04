from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.role_assignment import RoleAssignment
from app.services.authorization_event_emitter import (
    AuthorizationEventEmitter,
)


def _assignment() -> RoleAssignment:
    assignment = RoleAssignment(
        role_id="role-global-admin",
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
    assignment.first_seen_at = datetime.now(UTC)
    assignment.last_seen_at = datetime.now(UTC)
    assignment.is_active = True
    return assignment


def _db_with_role(role):
    db = MagicMock()

    def query(model):
        query = MagicMock()
        if model.__name__ == "Account":
            query.filter.return_value.one_or_none.return_value = (
                SimpleNamespace(
                    id="account-001",
                    identity_id="identity-001",
                    organizational_identity_id="org-identity-001",
                )
            )
        elif model.__name__ == "Role":
            query.filter.return_value.one_or_none.return_value = role
        return query

    db.query.side_effect = query
    return db


def _event_service():
    service = MagicMock()
    service.create_pending.side_effect = (
        lambda *, payload, actor: SimpleNamespace(
            payload=payload,
            actor=actor,
        )
    )
    return service


def test_emitter_applies_critical_materiality():
    role = SimpleNamespace(
        id="role-global-admin",
        name="Global Administrator",
        display_name="Global Administrator",
        system_name="Microsoft Entra ID",
        source_identifier=(
            "62e90394-69f5-4237-9190-012177145e10"
        ),
        privilege_level=None,
    )
    service = _event_service()
    emitter = AuthorizationEventEmitter(
        _db_with_role(role),
        organization_id="organization-027",
        event_service=service,
        work_item_generator=MagicMock(),
    )

    result = emitter.emit_role_assigned(
        assignment=_assignment(),
    )

    assert result.payload.risk_level == "Critical"
    assert result.payload.is_material is True
    assert (
        result.payload.evidence_json["classification"]["capability"]
        == "TenantAdministrator"
    )


def test_emitter_fails_safe_when_role_evidence_is_missing():
    service = _event_service()
    emitter = AuthorizationEventEmitter(
        _db_with_role(None),
        organization_id="organization-027",
        event_service=service,
        work_item_generator=MagicMock(),
    )

    result = emitter.emit_role_assigned(
        assignment=_assignment(),
    )

    assert result.payload.risk_level == "Unknown"
    assert result.payload.is_material is True
