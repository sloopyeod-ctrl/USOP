from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event_repository import AuditEventRepository


class AuditService:
    def __init__(self, db: Session):
        self.repository = AuditEventRepository(db)

    def record(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        message: str,
        actor: str | None = None,
        metadata: dict | None = None,
    ):
        event = AuditEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            message=message,
            metadata_json=metadata,
            source_system="USOP",
            confidence_score=100,
        )

        return self.repository.create(event)