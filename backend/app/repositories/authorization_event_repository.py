from sqlalchemy.orm import Session

from app.models.authorization_event import AuthorizationEvent


class AuthorizationEventRepository:
    """Persistence boundary for append-only AuthorizationEvent records."""

    def __init__(self, db: Session):
        self.db = db

    def create_pending(
        self,
        event: AuthorizationEvent,
    ) -> AuthorizationEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def get_by_id_for_organization(
        self,
        *,
        organization_id: str,
        event_id: str,
    ) -> AuthorizationEvent | None:
        return (
            self.db.query(AuthorizationEvent)
            .filter(
                AuthorizationEvent.organization_id == organization_id,
                AuthorizationEvent.id == event_id,
            )
            .one_or_none()
        )

    def list_for_organization(
        self,
        *,
        organization_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuthorizationEvent]:
        return (
            self.db.query(AuthorizationEvent)
            .filter(
                AuthorizationEvent.organization_id == organization_id
            )
            .order_by(
                AuthorizationEvent.detected_at.desc(),
                AuthorizationEvent.created_at.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
