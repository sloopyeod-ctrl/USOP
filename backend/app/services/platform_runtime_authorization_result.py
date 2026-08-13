from dataclasses import dataclass
from enum import Enum


class PlatformRuntimeAuthorizationDisposition(str, Enum):
    ALLOW = "Allow"
    DENY = "Deny"


@dataclass(frozen=True)
class PlatformRuntimeAuthorizationResult:
    disposition: PlatformRuntimeAuthorizationDisposition
    organization_id: str
    platform_user_id: str
    permission_key: str
    reason: str
    platform_role_id: str | None = None
    platform_role_key: str | None = None
    platform_permission_id: str | None = None
    platform_role_assignment_id: str | None = None
    evidence: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return (
            self.disposition
            == PlatformRuntimeAuthorizationDisposition.ALLOW
        )
