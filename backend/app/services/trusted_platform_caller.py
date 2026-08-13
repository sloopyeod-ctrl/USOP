from __future__ import annotations

from dataclasses import dataclass

from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


@dataclass(frozen=True)
class TrustedPlatformCaller:
    """
    Trusted resolution of an authenticated external principal to one
    Organization-scoped PlatformUser.

    This object carries identity only. It does not imply authorization.
    """

    organization_id: str
    platform_user_id: str
    principal: TrustedExternalPrincipal
