from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class IdentityTimelineBuilder:
    def __init__(self, db: Session):
        self.db = db

    def build(self, identity_id: str):
        events = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.is_active == True)
            .order_by(AuditEvent.created_at.desc())
            .all()
        )

        timeline = []

        for event in events:

            metadata = event.metadata_json or {}

            if metadata.get("identity_id") != identity_id:
                continue

            timeline.append(
                {
                    "timestamp": event.created_at,
                    "event_type": event.event_type,
                    "message": event.message,
                    "actor": event.actor,
                    "confidence": event.confidence_score,
                }
            )

        return timeline