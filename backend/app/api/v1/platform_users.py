from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.runtime_permission import (
    require_platform_permission,
)
from app.database.session import get_db
from app.schemas.platform_role_assignment import (
    PlatformRoleAssignmentCreate,
    PlatformRoleAssignmentRead,
)
from app.schemas.platform_user import PlatformUserRead
from app.services.platform_authorization_service import (
    PlatformAuthorizationAssignmentConflictError,
    PlatformAuthorizationAssignmentNotFoundError,
    PlatformAuthorizationAssignmentWindowError,
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationOrganizationNotActiveError,
    PlatformAuthorizationOrganizationNotFoundError,
    PlatformAuthorizationRoleNotActiveError,
    PlatformAuthorizationRoleNotFoundError,
    PlatformAuthorizationService,
    PlatformAuthorizationUserNotAssignableError,
    PlatformAuthorizationUserNotFoundError,
)
from app.services.platform_user_service import (
    PlatformUserInvalidLifecycleTransitionError,
    PlatformUserLastEffectiveAdministratorError,
    PlatformUserNotFoundError,
    PlatformUserOrganizationBoundaryError,
    PlatformUserOrganizationNotFoundError,
    PlatformUserService,
)
from app.services.trusted_platform_caller import TrustedPlatformCaller


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


def _run_platform_user_lifecycle_operation(
    *,
    operation: str,
    organization_id: str,
    platform_user_id: str,
    caller: TrustedPlatformCaller,
    db: Session,
):
    """
    Invoke one protected Platform User lifecycle service operation.

    The router owns only HTTP adaptation. Lifecycle policy, actor trust,
    transaction handling, last-effective-administrator protection, and audit
    behavior remain authoritative in PlatformUserService.
    """

    service = PlatformUserService(db)

    try:
        return getattr(service, operation)(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
            trusted_caller=caller,
        )

    except (
        PlatformUserOrganizationNotFoundError,
        PlatformUserNotFoundError,
        PlatformUserOrganizationBoundaryError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested Platform User lifecycle target was not found.",
        ) from error

    except (
        PlatformUserInvalidLifecycleTransitionError,
        PlatformUserLastEffectiveAdministratorError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/{platform_user_id}/suspend",
    response_model=PlatformUserRead,
)
def suspend_platform_user(
    organization_id: str,
    platform_user_id: str,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
):
    return _run_platform_user_lifecycle_operation(
        operation="suspend",
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        caller=caller,
        db=db,
    )


@router.post(
    "/{platform_user_id}/reactivate",
    response_model=PlatformUserRead,
)
def reactivate_platform_user(
    organization_id: str,
    platform_user_id: str,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
):
    return _run_platform_user_lifecycle_operation(
        operation="reactivate",
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        caller=caller,
        db=db,
    )


@router.post(
    "/{platform_user_id}/disable",
    response_model=PlatformUserRead,
)
def disable_platform_user(
    organization_id: str,
    platform_user_id: str,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
):
    return _run_platform_user_lifecycle_operation(
        operation="disable",
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        caller=caller,
        db=db,
    )


@router.post(
    "/{platform_user_id}/roles",
    response_model=PlatformRoleAssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def assign_platform_role(
    organization_id: str,
    platform_user_id: str,
    payload: PlatformRoleAssignmentCreate,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
):
    service = PlatformAuthorizationService(db)

    try:
        return service.assign_role(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
            platform_role_id=payload.platform_role_id,
            expires_at=payload.expires_at,
            trusted_caller=caller,
        )

    except (
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationUserNotFoundError,
        PlatformAuthorizationRoleNotFoundError,
        PlatformAuthorizationOrganizationBoundaryError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested Platform authorization target was not found.",
        ) from error

    except PlatformAuthorizationAssignmentConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except (
        PlatformAuthorizationOrganizationNotActiveError,
        PlatformAuthorizationUserNotAssignableError,
        PlatformAuthorizationRoleNotActiveError,
        PlatformAuthorizationAssignmentWindowError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

@router.delete(
    "/{platform_user_id}/roles/{platform_role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_platform_role(
    organization_id: str,
    platform_user_id: str,
    platform_role_id: str,
    caller: TrustedPlatformCaller = Depends(
        require_platform_permission(
            "platform-administration.manage"
        )
    ),
    db: Session = Depends(get_db),
) -> None:
    service = PlatformAuthorizationService(db)

    try:
        service.remove_role(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
            platform_role_id=platform_role_id,
            trusted_caller=caller,
        )

    except (
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationUserNotFoundError,
        PlatformAuthorizationRoleNotFoundError,
        PlatformAuthorizationAssignmentNotFoundError,
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
