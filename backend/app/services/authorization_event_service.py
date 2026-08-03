from sqlalchemy.orm import Session

from app.models.authorization_event import AuthorizationEvent
from app.repositories.authorization_event_repository import (
    AuthorizationEventRepository,
)
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.authorization_event import AuthorizationEventCreate


class AuthorizationEventService:
    """
    Application service for append-only authorization evidence.

    This service intentionally exposes no update or delete workflow.
    Corrections must be represented by a new event.
    """

    def __init__(
        self,
        db: Session,
        *,
        repository: AuthorizationEventRepository | None = None,
        organization_repository: OrganizationRepository | None = None,
    ):
        self.db = db
        self.repository = repository or AuthorizationEventRepository(db)
        self.organization_repository = (
            organization_repository or OrganizationRepository(db)
        )

    @staticmethod
    def _required_text(
        value: str,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be blank")

        return normalized

    def _require_organization(self, organization_id: str) -> None:
        organization = self.organization_repository.get_by_id(
            organization_id
        )
        if organization is None:
            raise ValueError(
                "AuthorizationEvent references an unknown Organization."
            )

    def create_pending(
        self,
        *,
        payload: AuthorizationEventCreate,
        actor: str,
    ) -> AuthorizationEvent:
        organization_id = self._required_text(
            payload.organization_id,
            field_name="organization_id",
        )
        actor_name = self._required_text(
            actor,
            field_name="actor",
        )

        self._require_organization(organization_id)

        event = AuthorizationEvent(
            organization_id=organization_id,
            organizational_identity_id=(
                payload.organizational_identity_id
            ),
            identity_id=payload.identity_id,
            account_id=payload.account_id,
            role_assignment_id=payload.role_assignment_id,
            subject_type=self._required_text(
                payload.subject_type,
                field_name="subject_type",
            ),
            subject_id=self._required_text(
                payload.subject_id,
                field_name="subject_id",
            ),
            event_type=self._required_text(
                payload.event_type,
                field_name="event_type",
            ),
            assignment_type=payload.assignment_type,
            previous_status=payload.previous_status,
            current_status=payload.current_status,
            directory_scope=payload.directory_scope,
            application_scope=payload.application_scope,
            effective_start=payload.effective_start,
            effective_end=payload.effective_end,
            detected_at=payload.detected_at,
            risk_level=self._required_text(
                payload.risk_level,
                field_name="risk_level",
            ),
            is_material=payload.is_material,
            previous_state_json=payload.previous_state_json,
            current_state_json=payload.current_state_json,
            evidence_json=payload.evidence_json,
            source_system=payload.source_system,
            source_identifier=payload.source_identifier,
            confidence_score=payload.confidence_score,
            created_by=actor_name,
            updated_by=actor_name,
        )

        return self.repository.create_pending(event)

    def create(
        self,
        *,
        payload: AuthorizationEventCreate,
        actor: str,
    ) -> AuthorizationEvent:
        try:
            event = self.create_pending(
                payload=payload,
                actor=actor,
            )
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(
        self,
        *,
        organization_id: str,
        event_id: str,
    ) -> AuthorizationEvent | None:
        self._require_organization(organization_id)
        return self.repository.get_by_id_for_organization(
            organization_id=organization_id,
            event_id=event_id,
        )

    def list_for_organization(
        self,
        *,
        organization_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuthorizationEvent]:
        self._require_organization(organization_id)

        if limit < 1 or limit > 500:
            raise ValueError("limit must be between 1 and 500")
        if offset < 0:
            raise ValueError("offset cannot be negative")

        return self.repository.list_for_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )
