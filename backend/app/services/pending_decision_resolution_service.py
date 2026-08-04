from sqlalchemy.orm import Session

from app.schemas.decision_record import DecisionRecordAction
from app.services.decision_record_service import (
    DecisionRecordService,
)
from app.services.pending_decision_work_item_service import (
    PendingDecisionWorkItemConflictError,
    PendingDecisionWorkItemNotFoundError,
    PendingDecisionWorkItemService,
)


class PendingDecisionResolutionError(Exception):
    """Base error for accountable work resolution."""


class PendingDecisionResolutionNotFoundError(
    PendingDecisionResolutionError
):
    pass


class PendingDecisionResolutionConflictError(
    PendingDecisionResolutionError
):
    pass


class PendingDecisionResolutionService:
    """
    Atomically create one human DecisionRecord and resolve one work item.
    """

    def __init__(
        self,
        db: Session,
        *,
        decision_service: (
            DecisionRecordService | None
        ) = None,
        work_item_service: (
            PendingDecisionWorkItemService | None
        ) = None,
    ):
        self.db = db
        self.decision_service = (
            decision_service
            or DecisionRecordService(db)
        )
        self.work_item_service = (
            work_item_service
            or PendingDecisionWorkItemService(db)
        )

    def resolve_with_decision(
        self,
        *,
        organization_id: str,
        work_item_id: str,
        recommendation_id: str,
        action: DecisionRecordAction,
    ):
        try:
            work_item = self.work_item_service.get_by_id(
                organization_id=organization_id,
                work_item_id=work_item_id,
            )

            if work_item is None:
                raise PendingDecisionResolutionNotFoundError(
                    "Pending decision work item was not found."
                )

            if not work_item.identity_id:
                raise PendingDecisionResolutionConflictError(
                    "Pending decision work item has no Identity context."
                )

            if work_item.status == "Resolved":
                raise PendingDecisionResolutionConflictError(
                    "Pending decision work item is already resolved."
                )

            record = (
                self.decision_service
                .create_decision_record_pending(
                    organization_id=organization_id,
                    identity_id=work_item.identity_id,
                    recommendation_id=recommendation_id,
                    action=action,
                )
            )

            resolved = self.work_item_service.resolve_pending(
                organization_id=organization_id,
                work_item_id=work_item.id,
                decision_record_id=record.id,
                actor=action.actor,
            )

            self.db.commit()
            self.db.refresh(record)
            self.db.refresh(resolved)

            return record

        except PendingDecisionWorkItemNotFoundError as error:
            self.db.rollback()
            raise PendingDecisionResolutionNotFoundError(
                str(error)
            ) from error

        except PendingDecisionWorkItemConflictError as error:
            self.db.rollback()
            raise PendingDecisionResolutionConflictError(
                str(error)
            ) from error

        except Exception:
            self.db.rollback()
            raise
