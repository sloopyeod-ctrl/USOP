from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.knowledge_asset import (
    KnowledgeAssetCreate,
    KnowledgeAssetRead,
)
from app.services.knowledge_asset_service import (
    KnowledgeAssetDuplicateVersionError,
    KnowledgeAssetOrganizationNotFoundError,
    KnowledgeAssetService,
    KnowledgeAssetValidationError,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/knowledge-assets"
    ),
    tags=["Knowledge Assets"],
)


@router.post(
    "/",
    response_model=KnowledgeAssetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_asset(
    organization_id: str,
    data: KnowledgeAssetCreate,
    db: Session = Depends(get_db),
):
    """
    Create one versioned Organizational Memory asset.

    Validation, normalization, version allocation, persistence, transaction
    management, and audit creation remain KnowledgeAssetService
    responsibilities.

    Actor attribution remains server-controlled and is not accepted from the
    request contract.
    """

    service = KnowledgeAssetService(db)

    try:
        return service.create(
            organization_id=organization_id,
            title=data.title,
            guidance=data.guidance,
            category=data.category,
            status=data.status,
            summary=data.summary,
            source_system=data.source_system,
            source_identifier=data.source_identifier,
            confidence_score=data.confidence_score,
        )

    except KnowledgeAssetOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except KnowledgeAssetValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except KnowledgeAssetDuplicateVersionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=list[KnowledgeAssetRead],
)
def list_knowledge_assets(
    organization_id: str,
    db: Session = Depends(get_db),
):
    """
    Return all KnowledgeAssets belonging to one Organization.

    Result ordering is controlled by the Organizational Memory repository and
    service layers.
    """

    try:
        return (
            KnowledgeAssetService(db)
            .list_for_organization(
                organization_id
            )
        )

    except KnowledgeAssetOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{knowledge_asset_id}",
    response_model=KnowledgeAssetRead,
)
def get_knowledge_asset(
    organization_id: str,
    knowledge_asset_id: str,
    db: Session = Depends(get_db),
):
    """
    Return one KnowledgeAsset only within the requested Organization.

    Cross-Organization KnowledgeAssets are treated as not found so the API
    does not disclose their existence.
    """

    service = KnowledgeAssetService(db)

    try:
        knowledge_asset = service.get_by_id(
            organization_id=organization_id,
            knowledge_asset_id=knowledge_asset_id,
        )

    except KnowledgeAssetOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if knowledge_asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge Asset not found.",
        )

    return knowledge_asset
