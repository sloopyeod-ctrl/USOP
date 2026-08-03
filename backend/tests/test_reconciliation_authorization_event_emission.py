from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.role_assignment import RoleAssignment
from app.reconciliation.reconciliation_engine import ReconciliationEngine


def test_reconciliation_emits_created_role_assignment_event():
    db = MagicMock()
    emitter = MagicMock()
    engine = ReconciliationEngine(
        db,
        organization_id="organization-027",
        authorization_event_emitter=emitter,
    )

    engine._resolve_role_assignment_subject = MagicMock(
        return_value="account-001"
    )
    engine._resolve_role_assignment_role_id = MagicMock(
        return_value="role-001"
    )
    engine._find_existing_role_assignment = MagicMock(
        return_value=None
    )

    db.add.side_effect = lambda value: setattr(
        value,
        "id",
        "assignment-001",
    )

    summary = {
        "role_assignments_created": 0,
        "role_assignments_updated": 0,
        "role_assignments_skipped": 0,
    }

    engine._reconcile_role_assignments(
        [
            {
                "subject_type": "Account",
                "assignment_type": "Direct",
                "status": "Active",
                "directory_scope": "/",
                "source_system": "Microsoft Entra ID",
                "source_identifier": "provider-assignment-001",
            }
        ],
        summary,
    )

    assert summary["role_assignments_created"] == 1
    emitter.emit_role_assigned.assert_called_once()
    emitted_assignment = (
        emitter.emit_role_assigned.call_args.kwargs["assignment"]
    )
    assert isinstance(emitted_assignment, RoleAssignment)
    assert emitted_assignment.subject_id == "account-001"
    assert emitted_assignment.role_id == "role-001"


def test_reconciliation_checks_update_before_mutation():
    db = MagicMock()
    emitter = MagicMock()
    engine = ReconciliationEngine(
        db,
        organization_id="organization-027",
        authorization_event_emitter=emitter,
    )

    existing = SimpleNamespace(
        assignment_type="Direct",
        status="Active",
        directory_scope="/",
        application_scope=None,
    )

    engine._resolve_role_assignment_subject = MagicMock(
        return_value="account-001"
    )
    engine._resolve_role_assignment_role_id = MagicMock(
        return_value="role-001"
    )
    engine._find_existing_role_assignment = MagicMock(
        return_value=existing
    )
    engine._update_role_assignment = MagicMock()

    incoming = {
        "subject_type": "Account",
        "assignment_type": "Direct",
        "status": "Eligible",
        "directory_scope": "/",
        "application_scope": None,
    }
    summary = {
        "role_assignments_created": 0,
        "role_assignments_updated": 0,
        "role_assignments_skipped": 0,
    }

    engine._reconcile_role_assignments(
        [incoming],
        summary,
    )

    emitter.emit_role_updated_if_changed.assert_called_once_with(
        existing=existing,
        incoming=incoming,
    )
    engine._update_role_assignment.assert_called_once_with(
        existing=existing,
        assignment=incoming,
    )
