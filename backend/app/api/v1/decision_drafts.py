from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.decision_knowledge_intelligence_service import (
    DecisionKnowledgeIntelligenceIntegrityError,
)
from app.intelligence.drafting import (
    DecisionDraftIdentityNotFoundError,
    DecisionDraftIntelligenceService,
    DecisionDraftIntelligenceValidationError,
    DecisionDraftRecommendationNotFoundError,
)
from app.schemas.decision_draft import (
    DecisionDraftRead,
    DecisionDraftRequest,
)
from app.services.decision_knowledge_service import (
    DecisionKnowledgeDecisionNotFoundError,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/identities/"
        "{identity_id}/recommendations/"
        "{recommendation_id}/draft"
    ),
    tags=["Decision Drafts"],
)


@router.post(
    "/",
    response_model=DecisionDraftRead,
    status_code=status.HTTP_200_OK,
)
def create_decision_draft(
    organization_id: str,
    identity_id: str,
    recommendation_id: str,
    data: DecisionDraftRequest,
    db: Session = Depends(get_db),
):
    """
    Construct deterministic documentation for an analyst-selected decision.

    The endpoint is read-only with respect to authoritative organizational
    state. It does not record a decision, interpret policy, invoke AI,
    authorize enforcement, or modify customer systems.

    Draft content remains analyst-reviewable and must be explicitly submitted
    through the separate DecisionRecord workflow.
    """

    try:
        draft = (
            DecisionDraftIntelligenceService(
                db=db
            )
            .build_for_recommendation(
                organization_id=(
                    organization_id
                ),
                identity_id=identity_id,
                recommendation_id=(
                    recommendation_id
                ),
                decision_type=(
                    data.decision_type
                ),
            )
        )

    except (
        DecisionDraftIntelligenceValidationError
    ) as error:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error

    except (
        DecisionDraftIdentityNotFoundError,
        DecisionDraftRecommendationNotFoundError,
        DecisionKnowledgeDecisionNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except (
        DecisionKnowledgeIntelligenceIntegrityError
    ) as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error

    return DecisionDraftRead.from_draft(
        draft,
        draft_profile=(
            data.draft_profile
        ),
    )
