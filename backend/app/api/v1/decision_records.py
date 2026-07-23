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
from app.services.decision_record_service import (
    DecisionRecordService,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/decision-records"
    ),
    tags=["Decision Records"],
)


@router.get(
    "/",
    response_model=list[DecisionRecordRead],
)
def list_decision_records(
    organization_id: str,
    db: Session = Depends(get_db),
):
    return (
        DecisionRecordService(db)
        .list_for_organization(
            organization_id
        )
    )


@router.get(
    "/identity/{identity_id}",
    response_model=list[DecisionRecordRead],
)
def list_identity_decision_records(
    organization_id: str,
    identity_id: str,
    db: Session = Depends(get_db),
):
    return (
        DecisionRecordService(db)
        .by_identity(
            organization_id=organization_id,
            identity_id=identity_id,
        )
    )


@router.get(
    "/{decision_id}",
    response_model=DecisionRecordRead | None,
)
def get_decision_record(
    organization_id: str,
    decision_id: str,
    db: Session = Depends(get_db),
):
    return (
        DecisionRecordService(db)
        .get_by_id(
            organization_id=organization_id,
            decision_id=decision_id,
        )
    )


@router.post(
    "/identity/{identity_id}/recommendation/"
    "{recommendation_index}",
    response_model=DecisionRecordRead,
    status_code=status.HTTP_201_CREATED,
)
def create_decision_record(
    organization_id: str,
    identity_id: str,
    recommendation_index: int,
    action: DecisionRecordAction,
    db: Session = Depends(get_db),
):
    service = DecisionRecordService(db)

    try:
        return service.create_from_recommendation(
            organization_id=organization_id,
            identity_id=identity_id,
            recommendation_index=recommendation_index,
            action=action,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except IndexError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
