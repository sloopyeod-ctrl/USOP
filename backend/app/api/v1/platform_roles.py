from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.runtime_permission import require_platform_permission
from app.database.session import get_db
from app.schemas.platform_role import PlatformRoleRead
from app.schemas.platform_role_permission import (
    PlatformRolePermissionCreate,
    PlatformRolePermissionRead,
)
from app.services.platform_authorization_service import (
    PlatformAuthorizationMappingConflictError,
    PlatformAuthorizationMappingNotFoundError,
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationOrganizationNotActiveError,
    PlatformAuthorizationOrganizationNotFoundError,
    PlatformAuthorizationPermissionNotFoundError,
    PlatformAuthorizationProtectedPermissionError,
    PlatformAuthorizationRoleNotActiveError,
    PlatformAuthorizationRoleNotFoundError,
    PlatformAuthorizationService,
)
from app.services.trusted_platform_caller import TrustedPlatformCaller


router = APIRouter(
    prefix="/api/v1/organizations/{organization_id}/platform-roles",
    tags=["Platform Roles"],
)


@router.get(
    "/",
    response_model=list[PlatformRoleRead],
)
def list_platform_roles(
    organization_id: str,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
):
    service = PlatformAuthorizationService(db)

    try:
        return service.list_roles(
            organization_id=organization_id,
            trusted_caller=caller,
        )
    except (
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationOrganizationBoundaryError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested Platform authorization target was not found.",
        ) from error
    except PlatformAuthorizationOrganizationNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post(
    "/{platform_role_id}/permissions",
    response_model=PlatformRolePermissionRead,
    status_code=status.HTTP_201_CREATED,
)
def grant_platform_permission(
    organization_id: str,
    platform_role_id: str,
    payload: PlatformRolePermissionCreate,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission("platform-administration.manage")
    ),
    db: Session = Depends(get_db),
):
    service = PlatformAuthorizationService(db)

    try:
        return service.grant_permission(
            organization_id=organization_id,
            platform_role_id=platform_role_id,
            platform_permission_id=payload.platform_permission_id,
            trusted_caller=caller,
        )
    except (
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationRoleNotFoundError,
        PlatformAuthorizationPermissionNotFoundError,
        PlatformAuthorizationOrganizationBoundaryError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested Platform authorization target was not found.",
        ) from error
    except PlatformAuthorizationMappingConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except (
        PlatformAuthorizationOrganizationNotActiveError,
        PlatformAuthorizationRoleNotActiveError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/{platform_role_id}/permissions/{platform_permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_platform_permission(
    organization_id: str,
    platform_role_id: str,
    platform_permission_id: str,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission("platform-administration.manage")
    ),
    db: Session = Depends(get_db),
) -> None:
    service = PlatformAuthorizationService(db)

    try:
        service.remove_permission(
            organization_id=organization_id,
            platform_role_id=platform_role_id,
            platform_permission_id=platform_permission_id,
            trusted_caller=caller,
        )
    except (
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationRoleNotFoundError,
        PlatformAuthorizationPermissionNotFoundError,
        PlatformAuthorizationMappingNotFoundError,
        PlatformAuthorizationOrganizationBoundaryError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested Platform authorization target was not found.",
        ) from error
    except PlatformAuthorizationProtectedPermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except PlatformAuthorizationOrganizationNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
