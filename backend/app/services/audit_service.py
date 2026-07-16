from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event_repository import (
    AuditEventRepository,
)


class AuditService:
    """
    Backend authority for immutable audit-event construction.

    record_pending() participates in a caller-owned transaction.
    record() temporarily preserves committed behavior for legacy workflows.
    """

    def __init__(self, db: Session):
        self.repository = AuditEventRepository(db)

    @staticmethod
    def _build_event(
        *,
        event_type: str,
        entity_type: str,
        entity_id: str,
        message: str,
        actor: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:
        return AuditEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            message=message,
            metadata_json=metadata,
            source_system="USOP",
            confidence_score=100,
        )

    def record_pending(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity_id: str,
        message: str,
        actor: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:
        """
        Create an audit event inside the caller's current transaction.
        """

        event = self._build_event(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            message=message,
            metadata=metadata,
        )

        return self.repository.create_pending(event)

    def record(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity_id: str,
        message: str,
        actor: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:
        """
        Create and commit an audit event for legacy callers.

        New atomic workflows should use record_pending().
        """

        event = self._build_event(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            message=message,
            metadata=metadata,
        )

        return self.repository.create(event)
