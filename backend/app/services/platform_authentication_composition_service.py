from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_user_invitation_acceptance_service import (
    PlatformUserInvitationAcceptanceService,
)
from app.services.trusted_caller_identity_service import (
    TrustedCallerIdentityService,
)
from app.services.trusted_caller_resolution_result import (
    TrustedCallerResolutionDisposition,
    TrustedCallerResolutionResult,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


class PlatformAuthenticationCompositionError(ValueError):
    pass


class PlatformAuthenticationCompositionService:
    """
    Provider-neutral composition of caller resolution and first authentication.

    Normal runtime resolution remains strict: only an Active Platform User
    resolves to a TrustedPlatformCaller. Invitation acceptance is attempted
    only for a structured Invited lifecycle result.
    """

    def __init__(
        self,
        db: Session,
        *,
        trusted_caller_identity_service=None,
        invitation_acceptance_service=None,
    ):
        self.db = db
        self.trusted_caller_identity_service = (
            trusted_caller_identity_service
            or TrustedCallerIdentityService(db)
        )
        self.invitation_acceptance_service = (
            invitation_acceptance_service
            or PlatformUserInvitationAcceptanceService(db)
        )

    @staticmethod
    def _is_invited_resolution(
        resolution: TrustedCallerResolutionResult,
    ) -> bool:
        return (
            resolution.disposition
            == TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE
            and resolution.platform_user_status
            == PlatformUserStatus.INVITED.value
        )

    def resolve_or_accept_invitation(
        self,
        *,
        organization_id: str,
        principal: TrustedExternalPrincipal,
    ) -> TrustedCallerResolutionResult:
        if not isinstance(
            principal,
            TrustedExternalPrincipal,
        ):
            raise TypeError(
                "principal must be TrustedExternalPrincipal."
            )

        resolution = (
            self.trusted_caller_identity_service.resolve(
                organization_id=organization_id,
                principal=principal,
            )
        )

        if resolution.resolved:
            return resolution

        if not self._is_invited_resolution(
            resolution
        ):
            return resolution

        self.invitation_acceptance_service.accept(
            organization_id=organization_id,
            principal=principal,
        )

        post_acceptance = (
            self.trusted_caller_identity_service.resolve(
                organization_id=organization_id,
                principal=principal,
            )
        )

        if not post_acceptance.resolved:
            raise PlatformAuthenticationCompositionError(
                "Invitation acceptance completed but the "
                "trusted caller resolver did not resolve "
                "an Active caller."
            )

        return post_acceptance
