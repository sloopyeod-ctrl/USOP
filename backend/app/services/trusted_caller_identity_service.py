from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.platform_user_status import PlatformUserStatus
from app.repositories.platform_user_repository import PlatformUserRepository
from app.services.trusted_caller_resolution_result import (
    TrustedCallerResolutionDisposition,
    TrustedCallerResolutionResult,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


class TrustedCallerIdentityService:
    """
    Resolve an already-authenticated external principal to one active
    PlatformUser inside one explicitly selected Organization.

    This service performs no credential/token validation and grants no
    authorization. It is the provider-neutral bridge between a future
    authentication adapter and runtime RBAC.
    """

    def __init__(
        self,
        db: Session,
        *,
        platform_user_repository: PlatformUserRepository | None = None,
    ):
        self.db = db
        self.platform_user_repository = (
            platform_user_repository
            or PlatformUserRepository(db)
        )

    @staticmethod
    def _required(
        value: str,
        field_name: str,
    ) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError(f"{field_name} is required.")
        return normalized

    def resolve(
        self,
        *,
        organization_id: str,
        principal: TrustedExternalPrincipal,
    ) -> TrustedCallerResolutionResult:
        organization_id = self._required(
            organization_id,
            "organization_id",
        )

        if not isinstance(
            principal,
            TrustedExternalPrincipal,
        ):
            raise TypeError(
                "principal must be TrustedExternalPrincipal."
            )

        platform_user = (
            self.platform_user_repository
            .get_by_external_identity(
                organization_id=organization_id,
                identity_provider=principal.identity_provider,
                external_tenant_id=principal.external_tenant_id,
                external_subject_id=principal.external_subject_id,
            )
        )

        if platform_user is None:
            return TrustedCallerResolutionResult(
                disposition=(
                    TrustedCallerResolutionDisposition.NO_MATCH
                ),
                organization_id=organization_id,
                reason="NoPlatformUserForTrustedPrincipal",
                evidence=(
                    f"provider={principal.identity_provider}",
                    f"tenant={principal.external_tenant_id}",
                    f"subject={principal.external_subject_id}",
                ),
            )

        if not getattr(platform_user, "is_active", True):
            return TrustedCallerResolutionResult(
                disposition=(
                    TrustedCallerResolutionDisposition
                    .PLATFORM_USER_INACTIVE
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                platform_user_status=platform_user.status,
                reason="PlatformUserRecordInactive",
            )

        if platform_user.status != PlatformUserStatus.ACTIVE.value:
            return TrustedCallerResolutionResult(
                disposition=(
                    TrustedCallerResolutionDisposition
                    .PLATFORM_USER_NOT_ACTIVE
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                platform_user_status=platform_user.status,
                reason="PlatformUserLifecycleNotActive",
                evidence=(
                    f"status={platform_user.status}",
                ),
            )

        expected_issuer = str(
            platform_user.identity_issuer or ""
        ).strip()
        presented_issuer = str(
            principal.issuer or ""
        ).strip()

        if (
            expected_issuer
            and expected_issuer != presented_issuer
        ):
            return TrustedCallerResolutionResult(
                disposition=(
                    TrustedCallerResolutionDisposition
                    .ISSUER_MISMATCH
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                platform_user_status=platform_user.status,
                reason="TrustedPrincipalIssuerDoesNotMatchPlatformUser",
                evidence=(
                    f"expected_issuer={expected_issuer}",
                    f"presented_issuer={presented_issuer or '<missing>'}",
                ),
            )

        caller = TrustedPlatformCaller(
            organization_id=organization_id,
            platform_user_id=platform_user.id,
            principal=principal,
        )

        return TrustedCallerResolutionResult(
            disposition=(
                TrustedCallerResolutionDisposition.RESOLVED
            ),
            organization_id=organization_id,
            platform_user_id=platform_user.id,
            platform_user_status=platform_user.status,
            reason="TrustedPrincipalResolvedToActivePlatformUser",
            caller=caller,
            evidence=(
                f"provider={principal.identity_provider}",
                f"tenant={principal.external_tenant_id}",
                f"subject={principal.external_subject_id}",
                f"platform_user_id={platform_user.id}",
            ),
        )
