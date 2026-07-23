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
    DecisionKnowledgeIntelligenceService,
)
from app.schemas.decision_knowledge import (
    DecisionKnowledgeCreate,
    DecisionKnowledgeIntelligenceRead,
    DecisionKnowledgeRead,
)
from app.services.decision_knowledge_service import (
    DecisionKnowledgeAssetNotFoundError,
    DecisionKnowledgeDecisionNotFoundError,
    DecisionKnowledgeDuplicateError,
    DecisionKnowledgeService,
    DecisionKnowledgeValidationError,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/decision-records/"
        "{decision_record_id}/knowledge"
    ),
    tags=["Decision Knowledge"],
)


@router.post(
    "/",
    response_model=DecisionKnowledgeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_decision_knowledge(
    organization_id: str,
    decision_record_id: str,
    data: DecisionKnowledgeCreate,
    db: Session = Depends(get_db),
):
    """
    Link one governed KnowledgeAsset to one accountable DecisionRecord.

    Organization ownership and DecisionRecord identity come from the path.
    Actor attribution remains server-controlled.
    """

    service = DecisionKnowledgeService(db)

    try:
        return service.create(
            organization_id=organization_id,
            decision_record_id=decision_record_id,
            knowledge_asset_id=data.knowledge_asset_id,
            relationship_type=data.relationship_type,
        )

    except (
        DecisionKnowledgeDecisionNotFoundError,
        DecisionKnowledgeAssetNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except DecisionKnowledgeValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except DecisionKnowledgeDuplicateError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=list[
        DecisionKnowledgeIntelligenceRead
    ],
)
def list_decision_knowledge(
    organization_id: str,
    decision_record_id: str,
    db: Session = Depends(get_db),
):
    """
    Return analyst-ready Organizational Memory for one DecisionRecord.

    The backend assembles relationship meaning and governed knowledge so
    clients do not need additional KnowledgeAsset lookups.
    """

    try:
        return (
            DecisionKnowledgeIntelligenceService(db)
            .list_for_decision(
                organization_id=organization_id,
                decision_record_id=decision_record_id,
            )
        )

    except DecisionKnowledgeDecisionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        DecisionKnowledgeIntelligenceIntegrityError
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
