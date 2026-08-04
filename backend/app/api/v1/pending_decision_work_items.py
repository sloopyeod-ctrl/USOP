from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.pending_decision_work_item import (
    PendingDecisionWorkItemRead,
)
from app.services.pending_decision_work_item_service import (
    PendingDecisionWorkItemOrganizationNotFoundError,
    PendingDecisionWorkItemService,
    PendingDecisionWorkItemValidationError,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/pending-decision-work-items"
    ),
    tags=["Pending Decision Work Items"],
)


@router.get(
    "/",
    response_model=list[PendingDecisionWorkItemRead],
)
def list_pending_decision_work_items(
    organization_id: str,
    work_status: str | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    """
    Return Organization-scoped analyst work.

    The route remains source-agnostic and framework-neutral. Ordering and
    status filtering are controlled by the service and repository layers.
    """

    try:
        return (
            PendingDecisionWorkItemService(db)
            .list_for_organization(
                organization_id=organization_id,
                status=work_status,
            )
        )

    except PendingDecisionWorkItemOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PendingDecisionWorkItemValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
