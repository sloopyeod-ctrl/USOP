from __future__ import annotations

from fastapi import (
    Depends,
    HTTPException,
    Security,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.security.auth.EntraOidcAuthenticationAdapter import (
    EntraOidcAuthenticationAdapter,
    EntraOidcAuthenticationError,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)
from app.services.platform_authentication_composition_service import (
    PlatformAuthenticationCompositionError,
    PlatformAuthenticationCompositionService,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="Microsoft Entra Bearer",
    description=(
        "Microsoft Entra v2 access token issued for the USOP API."
    ),
)


def _authentication_configuration() -> EntraOidcValidationConfig:
    """
    Build fail-closed inbound authentication configuration.

    Microsoft Graph connector credentials are deliberately not reused here.
    They represent USOP -> Microsoft Graph application authentication, while
    these values represent caller -> USOP API authentication.
    """

    tenant_id = str(
        settings.usop_auth_entra_tenant_id or ""
    ).strip()
    audience = str(
        settings.usop_auth_entra_audience or ""
    ).strip()
    required_scope = str(
        settings.usop_auth_entra_required_scope or ""
    ).strip()

    if not tenant_id or not audience or not required_scope:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="USOP API authentication is not configured.",
        )

    return EntraOidcValidationConfig(
        tenant_id=tenant_id,
        audience=audience,
        required_scope=required_scope,
    )


def _authenticate_bearer_token(
    token: str,
) -> object:
    """
    Cryptographically authenticate one bearer token.

    This helper intentionally performs no Organization selection,
    PlatformUser resolution, authorization, Seat evaluation, or licensing.
    """

    config = _authentication_configuration()
    adapter = EntraOidcAuthenticationAdapter(config)

    try:
        return adapter.authenticate(token)

    except EntraOidcAuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token authentication failed.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def get_authenticated_platform_caller(
    organization_id: str,
    credentials: HTTPAuthorizationCredentials | None = Security(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> TrustedPlatformCaller:
    """
    Resolve one authenticated HTTP request to one Organization-scoped caller.

    SECURITY CONTRACT:
    - Organization scope comes only from the route path.
    - Caller identity comes only from a cryptographically validated bearer
      token.
    - The browser cannot submit a PlatformUser identifier.
    - A token valid for one external principal does not grant access to every
      Organization where USOP is deployed.
    - Runtime RBAC remains a separate authorization boundary.
    """

    normalized_organization_id = str(
        organization_id or ""
    ).strip()

    if not normalized_organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization context is required.",
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = str(credentials.credentials or "").strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    principal = _authenticate_bearer_token(token)

    try:
        resolution = (
            PlatformAuthenticationCompositionService(db)
            .resolve_or_accept_invitation(
                organization_id=normalized_organization_id,
                principal=principal,
            )
        )
    except PlatformAuthenticationCompositionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller is not authorized for this Organization.",
        ) from error

    caller = resolution.caller

    if caller is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller is not authorized for this Organization.",
        )

    if caller.organization_id != normalized_organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caller Organization context mismatch.",
        )

    return caller
