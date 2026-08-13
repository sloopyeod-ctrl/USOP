from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.authenticated_caller import (
    get_authenticated_platform_caller,
)
from app.database.session import get_db
from app.services.platform_runtime_authorization_service import (
    PlatformRuntimeAuthorizationService,
)
from app.services.trusted_platform_caller import TrustedPlatformCaller


def require_platform_permission(
    permission_key: str,
) -> Callable[..., TrustedPlatformCaller]:
    """
    Build a FastAPI dependency for one server-defined platform permission.

    SECURITY CONTRACT:
    - Caller identity is inherited from the authenticated caller dependency.
    - Organization scope is inherited from TrustedPlatformCaller.
    - PlatformUser ID is inherited from TrustedPlatformCaller.
    - The endpoint defines the required permission key server-side.
    - Runtime authorization failure is non-enumerating HTTP 403.
    """

    normalized_permission_key = str(
        permission_key or ""
    ).strip()

    if not normalized_permission_key:
        raise ValueError("permission_key is required.")

    def dependency(
        caller: TrustedPlatformCaller = Depends(
            get_authenticated_platform_caller
        ),
        db: Session = Depends(get_db),
    ) -> TrustedPlatformCaller:
        result = PlatformRuntimeAuthorizationService(
            db
        ).evaluate(
            organization_id=caller.organization_id,
            platform_user_id=caller.platform_user_id,
            permission_key=normalized_permission_key,
        )

        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Caller is not authorized for this operation.",
            )

        # Defense in depth: an ALLOW result must describe exactly the caller
        # and permission evaluated by this dependency.
        if (
            result.organization_id != caller.organization_id
            or result.platform_user_id != caller.platform_user_id
            or result.permission_key != normalized_permission_key
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authorization result context mismatch.",
            )

        return caller

    return dependency
