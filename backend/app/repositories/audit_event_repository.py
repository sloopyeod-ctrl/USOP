from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class AuditEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event: AuditEvent):
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_all(self):
        return (
            self.db.query(AuditEvent)
            .order_by(AuditEvent.created_at.desc())
            .all()
        )

    def by_entity(self, entity_type: str, entity_id: str):
        return (
            self.db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id,
            )
            .order_by(AuditEvent.created_at.desc())
            .all()
        )