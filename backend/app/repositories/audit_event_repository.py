from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class AuditEventRepository:
    """
    Persistence boundary for append-only USOP AuditEvent records.

    New atomic workflows should use create_pending(), leaving commit and
    rollback ownership to the service coordinating the complete operation.

    create() temporarily preserves the legacy committed behavior for existing
    callers. It will be removed after those workflows are migrated and tested.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_pending(
        self,
        event: AuditEvent,
    ) -> AuditEvent:
        """
        Add an AuditEvent to the current transaction without committing.

        The calling service owns commit or rollback.
        """

        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)

        return event

    def create(
        self,
        event: AuditEvent,
    ) -> AuditEvent:
        """
        Persist and commit an AuditEvent for legacy callers.

        Deprecated for new workflows. Use create_pending() when the audit event
        must participate atomically with other persistence operations.
        """

        event = self.create_pending(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def list_all(self) -> list[AuditEvent]:
        return (
            self.db.query(AuditEvent)
            .order_by(
                AuditEvent.created_at.desc(),
            )
            .all()
        )

    def by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[AuditEvent]:
        return (
            self.db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id,
            )
            .order_by(
                AuditEvent.created_at.desc(),
            )
            .all()
        )
