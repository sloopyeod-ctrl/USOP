from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.domain.principal_type import PrincipalType
from app.models.account import Account
from app.models.role_assignment import RoleAssignment
from app.schemas.authorization_event import AuthorizationEventCreate
from app.services.authorization_event_service import AuthorizationEventService


SYSTEM_AUTHORIZATION_EVENT_ACTOR = "system:reconciliation"

_TRACKED_ROLE_ASSIGNMENT_FIELDS = (
    "assignment_type",
    "status",
    "directory_scope",
    "application_scope",
)


class AuthorizationEventEmitter:
    """
    Translate proven RoleAssignment reconciliation changes into append-only
    AuthorizationEvent evidence.

    This emitter records facts only. It does not classify materiality, create
    analyst work, or make recommendations.
    """

    def __init__(
        self,
        db: Session,
        *,
        organization_id: str | None,
        event_service: AuthorizationEventService | None = None,
    ):
        self.db = db
        self.organization_id = (
            organization_id.strip()
            if organization_id
            else None
        )
        self.event_service = event_service or AuthorizationEventService(db)

    @staticmethod
    def _state_from_assignment(
        assignment: RoleAssignment,
    ) -> dict[str, Any]:
        return {
            "role_id": assignment.role_id,
            "subject_type": assignment.subject_type,
            "subject_id": assignment.subject_id,
            "assignment_type": assignment.assignment_type,
            "status": assignment.status,
            "directory_scope": assignment.directory_scope,
            "application_scope": assignment.application_scope,
            "source_system": assignment.source_system,
            "source_identifier": assignment.source_identifier,
            "first_seen_at": assignment.first_seen_at,
            "last_seen_at": assignment.last_seen_at,
            "confidence_score": assignment.confidence_score,
            "is_active": assignment.is_active,
        }

    @staticmethod
    def _normalized_current_state(
        existing: RoleAssignment,
        incoming: dict,
    ) -> dict[str, Any]:
        return {
            "role_id": existing.role_id,
            "subject_type": existing.subject_type,
            "subject_id": existing.subject_id,
            "assignment_type": incoming.get(
                "assignment_type",
                existing.assignment_type,
            ),
            "status": incoming.get(
                "status",
                existing.status,
            ),
            "directory_scope": incoming.get("directory_scope"),
            "application_scope": incoming.get("application_scope"),
            "source_system": incoming.get(
                "source_system",
                incoming.get(
                    "source",
                    existing.source_system,
                ),
            ),
            "source_identifier": incoming.get(
                "source_identifier",
                existing.source_identifier,
            ),
            "first_seen_at": incoming.get(
                "first_seen_at",
                existing.first_seen_at,
            ),
            "last_seen_at": incoming.get(
                "last_seen_at",
                existing.last_seen_at,
            ),
            "confidence_score": incoming.get(
                "confidence_score",
                existing.confidence_score,
            ),
            "is_active": True,
        }

    @staticmethod
    def _tracked_changes(
        previous_state: dict[str, Any],
        current_state: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        changes: dict[str, dict[str, Any]] = {}

        for field_name in _TRACKED_ROLE_ASSIGNMENT_FIELDS:
            previous_value = previous_state.get(field_name)
            current_value = current_state.get(field_name)

            if previous_value != current_value:
                changes[field_name] = {
                    "previous": previous_value,
                    "current": current_value,
                }

        return changes

    def _account_context(
        self,
        assignment: RoleAssignment,
    ) -> tuple[str | None, str | None, str | None]:
        if assignment.subject_type != PrincipalType.ACCOUNT.value:
            return None, None, None

        account = (
            self.db.query(Account)
            .filter(Account.id == assignment.subject_id)
            .one_or_none()
        )

        if account is None:
            return None, None, None

        return (
            account.id,
            account.identity_id,
            account.organizational_identity_id,
        )

    def _emit(
        self,
        *,
        event_type: str,
        assignment: RoleAssignment,
        previous_state: dict[str, Any] | None,
        current_state: dict[str, Any],
        evidence_json: dict[str, Any],
        detected_at: datetime | None = None,
    ):
        if not self.organization_id:
            return None

        account_id, identity_id, organizational_identity_id = (
            self._account_context(assignment)
        )

        payload = AuthorizationEventCreate(
            organization_id=self.organization_id,
            organizational_identity_id=organizational_identity_id,
            identity_id=identity_id,
            account_id=account_id,
            role_assignment_id=assignment.id,
            subject_type=assignment.subject_type,
            subject_id=assignment.subject_id,
            event_type=event_type,
            assignment_type=current_state.get("assignment_type"),
            previous_status=(
                previous_state.get("status")
                if previous_state is not None
                else None
            ),
            current_status=current_state.get("status"),
            directory_scope=current_state.get("directory_scope"),
            application_scope=current_state.get("application_scope"),
            effective_start=current_state.get("first_seen_at"),
            effective_end=None,
            detected_at=detected_at or datetime.now(UTC),
            risk_level="Low",
            is_material=False,
            previous_state_json=previous_state,
            current_state_json=current_state,
            evidence_json=evidence_json,
            source_system=assignment.source_system,
            source_identifier=assignment.source_identifier,
            confidence_score=assignment.confidence_score,
        )

        return self.event_service.create_pending(
            payload=payload,
            actor=SYSTEM_AUTHORIZATION_EVENT_ACTOR,
        )

    def emit_role_assigned(
        self,
        *,
        assignment: RoleAssignment,
        detected_at: datetime | None = None,
    ):
        current_state = self._state_from_assignment(assignment)

        return self._emit(
            event_type="ROLE_ASSIGNED",
            assignment=assignment,
            previous_state=None,
            current_state=current_state,
            evidence_json={
                "change_kind": "created",
                "tracked_fields": list(
                    _TRACKED_ROLE_ASSIGNMENT_FIELDS
                ),
            },
            detected_at=detected_at,
        )

    def emit_role_updated_if_changed(
        self,
        *,
        existing: RoleAssignment,
        incoming: dict,
        detected_at: datetime | None = None,
    ):
        previous_state = self._state_from_assignment(existing)
        current_state = self._normalized_current_state(
            existing,
            incoming,
        )
        changes = self._tracked_changes(
            previous_state,
            current_state,
        )

        if not changes:
            return None

        return self._emit(
            event_type="ROLE_UPDATED",
            assignment=existing,
            previous_state=previous_state,
            current_state=current_state,
            evidence_json={
                "change_kind": "updated",
                "changes": changes,
            },
            detected_at=detected_at,
        )
