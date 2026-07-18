from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.platform_bootstrap import (
    PlatformBootstrapRequest,
    PlatformBootstrapResult,
)
from app.services.platform_bootstrap_service import (
    PlatformBootstrapConflictError,
    PlatformBootstrapService,
    PlatformBootstrapServiceError,
)
from app.services.platform_user_service import (
    PlatformUserBootstrapAlreadyCompletedError,
    PlatformUserExternalIdentityConflictError,
    PlatformUserLicenseNotEligibleError,
    PlatformUserOrganizationNotActiveError,
    PlatformUserOrganizationNotFoundError,
    PlatformUserServiceError,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/platform-bootstrap"
    ),
    tags=["Platform Bootstrap"],
)


@router.post(
    "/",
    response_model=PlatformBootstrapResult,
    status_code=status.HTTP_201_CREATED,
)
def bootstrap_platform_administrator(
    organization_id: str,
    data: PlatformBootstrapRequest,
    db: Session = Depends(get_db),
) -> PlatformBootstrapResult:
    """
    Atomically create the first Platform Administrator and canonical authority.

    Organization scope comes from the route. Licensing, role creation,
    permission creation, authorization, audit attribution, transaction
    ownership, and rollback behavior remain controlled by the backend.
    """

    try:
        return (
            PlatformBootstrapService(db)
            .bootstrap_platform_administrator(
                organization_id=organization_id,
                display_name=data.display_name,
                email=str(data.email),
                identity_provider=data.identity_provider,
                external_tenant_id=(
                    data.external_tenant_id
                ),
                external_subject_id=(
                    data.external_subject_id
                ),
                identity_issuer=data.identity_issuer,
            )
        )

    except PlatformUserOrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        PlatformUserOrganizationNotActiveError,
        PlatformUserLicenseNotEligibleError,
        PlatformUserBootstrapAlreadyCompletedError,
        PlatformUserExternalIdentityConflictError,
        PlatformBootstrapConflictError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except (
        PlatformUserServiceError,
        PlatformBootstrapServiceError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
