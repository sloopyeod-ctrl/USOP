from __future__ import annotations

from datetime import UTC, datetime
from sqlalchemy.orm import Session

from app.domain.platform_user_status import PlatformUserStatus
from app.repositories.platform_user_repository import PlatformUserRepository
from app.services.audit_service import AuditService
from app.services.trusted_external_principal import TrustedExternalPrincipal

ACTOR_PREFIX = "authenticated-external-principal:"


class PlatformUserInvitationAcceptanceError(ValueError):
    pass


class PlatformUserInvitationNotFoundError(
    PlatformUserInvitationAcceptanceError
):
    pass


class PlatformUserInvitationNotAcceptableError(
    PlatformUserInvitationAcceptanceError
):
    pass


class PlatformUserInvitationIssuerMismatchError(
    PlatformUserInvitationAcceptanceError
):
    pass


class PlatformUserInvitationAcceptanceService:
    def __init__(
        self,
        db: Session,
        *,
        platform_user_repository=None,
        audit_service=None,
    ):
        self.db = db
        self.platform_user_repository = (
            platform_user_repository
            or PlatformUserRepository(db)
        )
        self.audit_service = (
            audit_service
            or AuditService(db)
        )

    def accept(
        self,
        *,
        organization_id: str,
        principal: TrustedExternalPrincipal,
    ):
        organization_id = str(
            organization_id or ""
        ).strip()

        if not organization_id:
            raise ValueError(
                "organization_id is required."
            )

        if not isinstance(
            principal,
            TrustedExternalPrincipal,
        ):
            raise TypeError(
                "principal must be TrustedExternalPrincipal."
            )

        authenticated_at = (
            principal.authenticated_at
            or datetime.now(UTC)
        )

        if authenticated_at.tzinfo is None:
            authenticated_at = authenticated_at.replace(
                tzinfo=UTC
            )
        else:
            authenticated_at = authenticated_at.astimezone(
                UTC
            )

        try:
            platform_user = (
                self.platform_user_repository
                .get_by_external_identity_for_update(
                    organization_id=organization_id,
                    identity_provider=principal.identity_provider,
                    external_tenant_id=principal.external_tenant_id,
                    external_subject_id=principal.external_subject_id,
                )
            )

            if platform_user is None:
                raise PlatformUserInvitationNotFoundError(
                    "No Platform User invitation matches the "
                    "authenticated external principal."
                )

            if not getattr(
                platform_user,
                "is_active",
                True,
            ):
                raise PlatformUserInvitationNotAcceptableError(
                    "Platform User record is inactive."
                )

            if (
                platform_user.status
                != PlatformUserStatus.INVITED.value
            ):
                raise PlatformUserInvitationNotAcceptableError(
                    "Platform User is not in Invited lifecycle state."
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
                raise PlatformUserInvitationIssuerMismatchError(
                    "Authenticated principal issuer does not "
                    "match the Platform User invitation."
                )

            actor = (
                f"{ACTOR_PREFIX}"
                f"{principal.identity_provider}:"
                f"{principal.external_tenant_id}:"
                f"{principal.external_subject_id}"
            )

            platform_user = (
                self.platform_user_repository
                .record_first_authentication(
                    platform_user=platform_user,
                    activated_at=authenticated_at,
                    updated_by=actor,
                )
            )

            audit_event = self.audit_service.record_pending(
                event_type="PlatformUserInvitationAccepted",
                entity_type="PlatformUser",
                entity_id=platform_user.id,
                actor=actor,
                message=(
                    f"Platform User "
                    f"'{platform_user.display_name}' "
                    "accepted the invitation through "
                    "authenticated external identity."
                ),
                metadata={
                    "organization_id": organization_id,
                    "identity_provider": (
                        principal.identity_provider
                    ),
                    "external_tenant_id": (
                        principal.external_tenant_id
                    ),
                    "external_subject_id": (
                        principal.external_subject_id
                    ),
                    "identity_issuer": principal.issuer,
                    "previous_status": (
                        PlatformUserStatus.INVITED.value
                    ),
                    "new_status": (
                        PlatformUserStatus.ACTIVE.value
                    ),
                    "authenticated_at": (
                        authenticated_at.isoformat()
                    ),
                    "authentication_completed": True,
                    "authorization_granted_by_transition": False,
                    "seat_allocated_by_transition": False,
                },
            )

            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)

            return platform_user

        except Exception:
            self.db.rollback()
            raise
