from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.decision_pattern_intelligence_service import (
    DecisionPatternIntelligenceService,
    DecisionPatternIntelligenceValidationError,
)
from app.schemas.decision_pattern import (
    DecisionPatternRead,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/identities/"
        "{identity_id}/recommendations/"
        "{recommendation_id}/patterns"
    ),
    tags=["Decision Patterns"],
)


@router.get(
    "/",
    response_model=list[DecisionPatternRead],
)
def list_decision_patterns(
    organization_id: str,
    identity_id: str,
    recommendation_id: str,
    db: Session = Depends(get_db),
):
    """
    Return deterministic organizational patterns for one recommendation.

    The endpoint is read-only. Pattern intelligence describes observed
    decision history and does not interpret organizational policy, prescribe
    an action, authorize enforcement, or modify customer systems.
    """

    try:
        patterns = (
            DecisionPatternIntelligenceService(db)
            .analyze_recommendation(
                organization_id=organization_id,
                identity_id=identity_id,
                recommendation_id=recommendation_id,
            )
        )

    except (
        DecisionPatternIntelligenceValidationError
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return [
        DecisionPatternRead.model_validate(
            pattern.to_dict()
        )
        for pattern in patterns
    ]
