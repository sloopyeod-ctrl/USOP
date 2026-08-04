from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.decision_record import (
    DecisionRecordAction,
    DecisionRecordRead,
)
from app.services.pending_decision_resolution_service import (
    PendingDecisionResolutionConflictError,
    PendingDecisionResolutionNotFoundError,
    PendingDecisionResolutionService,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/pending-decision-work-items"
    ),
    tags=["Pending Decision Resolution"],
)


@router.post(
    (
        "/{work_item_id}/recommendations/"
        "{recommendation_id}/decision"
    ),
    response_model=DecisionRecordRead,
    status_code=status.HTTP_201_CREATED,
)
def resolve_pending_decision_with_record(
    organization_id: str,
    work_item_id: str,
    recommendation_id: str,
    action: DecisionRecordAction,
    db: Session = Depends(get_db),
):
    """
    Atomically create a human decision and resolve pending work.
    """

    try:
        return (
            PendingDecisionResolutionService(db)
            .resolve_with_decision(
                organization_id=organization_id,
                work_item_id=work_item_id,
                recommendation_id=recommendation_id,
                action=action,
            )
        )

    except PendingDecisionResolutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PendingDecisionResolutionConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
