from sqlalchemy.orm import Session

from app.models.pending_decision_work_item import (
    PendingDecisionWorkItem,
)


class PendingDecisionWorkItemRepository:
    """Persistence boundary for analyst decision work."""

    def __init__(self, db: Session):
        self.db = db

    def create_pending(
        self,
        work_item: PendingDecisionWorkItem,
    ) -> PendingDecisionWorkItem:
        self.db.add(work_item)
        self.db.flush()
        return work_item

    def get_by_source_for_organization(
        self,
        *,
        organization_id: str,
        source_type: str,
        source_id: str,
    ) -> PendingDecisionWorkItem | None:
        return (
            self.db.query(PendingDecisionWorkItem)
            .filter(
                PendingDecisionWorkItem.organization_id
                == organization_id,
                PendingDecisionWorkItem.source_type
                == source_type,
                PendingDecisionWorkItem.source_id
                == source_id,
            )
            .one_or_none()
        )

    def get_by_id_for_organization(
        self,
        *,
        organization_id: str,
        work_item_id: str,
    ) -> PendingDecisionWorkItem | None:
        return (
            self.db.query(PendingDecisionWorkItem)
            .filter(
                PendingDecisionWorkItem.organization_id
                == organization_id,
                PendingDecisionWorkItem.id
                == work_item_id,
                PendingDecisionWorkItem.is_active.is_(True),
            )
            .one_or_none()
        )

    def list_for_organization(
        self,
        *,
        organization_id: str,
        status: str | None = None,
    ) -> list[PendingDecisionWorkItem]:
        query = (
            self.db.query(PendingDecisionWorkItem)
            .filter(
                PendingDecisionWorkItem.organization_id
                == organization_id,
                PendingDecisionWorkItem.is_active.is_(True),
            )
        )

        if status is not None:
            query = query.filter(
                PendingDecisionWorkItem.status == status
            )

        return (
            query.order_by(
                PendingDecisionWorkItem.created_at.desc(),
                PendingDecisionWorkItem.id.asc(),
            )
            .all()
        )
