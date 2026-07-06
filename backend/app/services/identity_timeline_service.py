from datetime import UTC, datetime
from sqlalchemy.orm import Session

from app.models.access_review import AccessReview
from app.models.audit_event import AuditEvent
from app.models.identity import Identity


class IdentityTimelineService:
    def __init__(self, db: Session):
        self.db = db

    def get_timeline(self, identity_id: str):
        identity = (
            self.db.query(Identity)
            .filter(
                Identity.id == identity_id,
                Identity.is_active == True,
            )
            .first()
        )

        if identity is None:
            return None

        events = []

        events.append(
            {
                "timestamp": identity.created_at,
                "event_type": "IdentityCreated",
                "source": "Identity",
                "message": f"Identity created for {identity.display_name}.",
                "metadata": {
                    "identity_id": identity.id,
                    "display_name": identity.display_name,
                    "primary_email": identity.primary_email,
                },
            }
        )

        reviews = (
            self.db.query(AccessReview)
            .filter(
                AccessReview.identity_id == identity_id,
                AccessReview.is_active == True,
            )
            .all()
        )

        for review in reviews:
            events.append(
                {
                    "timestamp": review.created_at,
                    "event_type": "AccessReviewCreated",
                    "source": "AccessReview",
                    "message": f"Access review created with status {review.status}.",
                    "metadata": {
                        "review_id": review.id,
                        "campaign_id": review.campaign_id,
                        "risk_score": review.risk_score,
                        "risk_level": review.risk_level,
                        "reason": review.reason,
                    },
                }
            )

            if review.reviewed_at:
                events.append(
                    {
                        "timestamp": review.reviewed_at,
                        "event_type": f"AccessReview{review.status}",
                        "source": "AccessReview",
                        "message": f"Access review {review.status} by {review.reviewed_by}.",
                        "metadata": {
                            "review_id": review.id,
                            "reviewed_by": review.reviewed_by,
                            "notes": review.notes,
                        },
                    }
                )

        audit_events = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.is_active == True)
            .all()
        )

        audit_events = [
            event
            for event in audit_events
            if event.metadata_json
            and event.metadata_json.get("identity_id") == identity_id
        ]

        for event in audit_events:
            events.append(
                {
                    "timestamp": event.created_at,
                    "event_type": event.event_type,
                    "source": "AuditEvent",
                    "message": event.message,
                    "metadata": event.metadata_json,
                }
            )

        def normalize_timestamp(value):
            if value is None:
                return datetime.min.replace(tzinfo=UTC)

            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)

            return value

        return sorted(
            events,
            key=lambda item: normalize_timestamp(item["timestamp"]),
            reverse=True,
        )