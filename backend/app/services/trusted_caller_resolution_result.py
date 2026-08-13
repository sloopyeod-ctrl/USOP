from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.services.trusted_platform_caller import TrustedPlatformCaller


class TrustedCallerResolutionDisposition(str, Enum):
    RESOLVED = "Resolved"
    NO_MATCH = "NoMatch"
    PLATFORM_USER_INACTIVE = "PlatformUserInactive"
    PLATFORM_USER_NOT_ACTIVE = "PlatformUserNotActive"
    ISSUER_MISMATCH = "IssuerMismatch"


@dataclass(frozen=True)
class TrustedCallerResolutionResult:
    disposition: TrustedCallerResolutionDisposition
    organization_id: str
    reason: str
    caller: TrustedPlatformCaller | None = None
    platform_user_id: str | None = None
    evidence: tuple[str, ...] = ()

    @property
    def resolved(self) -> bool:
        return (
            self.disposition
            == TrustedCallerResolutionDisposition.RESOLVED
            and self.caller is not None
        )
