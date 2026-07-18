from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.platform_user import PlatformUserRead
from app.services.platform_user_service import (
    PlatformUserOrganizationNotFoundError,
    PlatformUserService,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/platform-users"
    ),
    tags=["Platform Users"],
)


@router.get(
    "/",
    response_model=list[PlatformUserRead],
)
def list_platform_users(
    organization_id: str,
    db: Session = Depends(get_db),
):
    """
    Return Platform Users belonging to one Organization.

    Authentication, authorization, and Seat enforcement remain separate
    concerns and are not implemented by this read-only endpoint.
    """

    try:
        return (
            PlatformUserService(db)
            .list_for_organization(
                organization_id
            )
        )

    except PlatformUserOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/{platform_user_id}",
    response_model=PlatformUserRead,
)
def get_platform_user(
    organization_id: str,
    platform_user_id: str,
    db: Session = Depends(get_db),
):
    """
    Return one Platform User only within the requested Organization.

    Cross-Organization Platform Users are treated as not found.
    """

    service = PlatformUserService(db)

    try:
        platform_user = service.get_by_id(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
        )

    except PlatformUserOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if platform_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform User not found.",
        )

    return platform_user
