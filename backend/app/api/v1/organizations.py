from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationRead,
)
from app.services.organization_service import (
    OrganizationConflictError,
    OrganizationService,
)


router = APIRouter(
    prefix="/api/v1/organizations",
    tags=["Organizations"],
)


@router.post(
    "/",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
):
    """
    Bootstrap a canonical USOP Organization.

    Actor attribution is assigned by the backend. The request cannot supply
    or override the audit actor.
    """

    service = OrganizationService(db)

    try:
        return service.create(data)
    except OrganizationConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=list[OrganizationRead],
)
def list_organizations(
    db: Session = Depends(get_db),
):
    return OrganizationService(db).list_all()


@router.get(
    "/slug/{slug}",
    response_model=OrganizationRead,
)
def get_organization_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    organization = (
        OrganizationService(db)
        .get_by_slug(slug)
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization


@router.get(
    "/{organization_id}",
    response_model=OrganizationRead,
)
def get_organization(
    organization_id: str,
    db: Session = Depends(get_db),
):
    organization = (
        OrganizationService(db)
        .get_by_id(organization_id)
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization
