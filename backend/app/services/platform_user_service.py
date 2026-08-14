from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.organization_status import OrganizationStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.models.platform_user import PlatformUser
from app.repositories.license_repository import LicenseRepository
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.platform_user_repository import (
    PlatformUserRepository,
)
from app.services.audit_service import AuditService
from app.services.platform_runtime_authorization_service import (
    PlatformRuntimeAuthorizationService,
)
from app.services.trusted_platform_caller import TrustedPlatformCaller


SYSTEM_PLATFORM_BOOTSTRAP_ACTOR = "USOP System Bootstrap"
AUTHENTICATED_PLATFORM_USER_ACTOR_PREFIX = "platform-user:"
PLATFORM_ADMINISTRATION_PERMISSION_KEY = "platform-administration.manage"


class PlatformUserServiceError(ValueError):
    """Base exception for Platform User service failures."""


class PlatformUserOrganizationNotFoundError(
    PlatformUserServiceError
):
    """Raised when bootstrap references an unknown Organization."""


class PlatformUserOrganizationNotActiveError(
    PlatformUserServiceError
):
    """Raised when bootstrap targets a non-active Organization."""


class PlatformUserLicenseNotEligibleError(
    PlatformUserServiceError
):
    """Raised when no structurally eligible Bootstrap License exists."""


class PlatformUserBootstrapAlreadyCompletedError(
    PlatformUserServiceError
):
    """Raised when any Platform User already exists for the Organization."""


class PlatformUserExternalIdentityConflictError(
    PlatformUserServiceError
):
    """Raised when the external identity binding cannot be created."""


class PlatformUserNotFoundError(
    PlatformUserServiceError
):
    """Raised when a lifecycle target is not found in the Organization."""


class PlatformUserOrganizationBoundaryError(
    PlatformUserServiceError
):
    """Raised when trusted actor context crosses an Organization boundary."""


class PlatformUserInvalidLifecycleTransitionError(
    PlatformUserServiceError
):
    """Raised when a requested Platform User lifecycle transition is invalid."""


class PlatformUserLastEffectiveAdministratorError(
    PlatformUserServiceError
):
    """Raised when a lifecycle mutation would remove the last effective admin."""


class PlatformUserService:
    """
    Backend authority for USOP Platform User lifecycle workflows.

    The first capability is one-time administrator bootstrap. Bootstrap creates
    an initial operator identity only. It does not authenticate the user,
    assign Platform roles, allocate a commercial Seat, validate an identity
    token, or grant authorization by virtue of bootstrap provenance.
    """

    def __init__(self, db: Session):
        self.db = db
        self.organization_repository = OrganizationRepository(db)
        self.license_repository = LicenseRepository(db)
        self.platform_user_repository = PlatformUserRepository(db)
        self.audit_service = AuditService(db)
        self.runtime_authorization_service = (
            PlatformRuntimeAuthorizationService(db)
        )

    def _bootstrap_first_administrator_pending(
        self,
        *,
        organization_id: str,
        display_name: str,
        email: str,
        identity_provider: str,
        external_tenant_id: str,
        external_subject_id: str,
        identity_issuer: str | None = None,
        actor: str = SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
        evaluated_at: datetime | None = None,
        authorization_granted: bool = False,
    ):
        """
        Create the first audited Platform User without committing.

        The Organization row is locked so concurrent bootstrap attempts for
        the same Organization are serialized. The calling service owns the
        database commit, refresh, and rollback operations.
        """

        now = evaluated_at or datetime.now(UTC)

        organization = (
            self.organization_repository
            .get_by_id_for_update(
                organization_id
            )
        )

        if organization is None:
            raise PlatformUserOrganizationNotFoundError(
                "The Platform User references an unknown Organization."
            )

        if organization.status != OrganizationStatus.ACTIVE.value:
            raise PlatformUserOrganizationNotActiveError(
                "Platform Administrator bootstrap requires "
                "an active Organization."
            )

        eligible_license = (
            self.license_repository
            .get_bootstrap_eligible_license(
                organization.id,
                evaluated_at=now,
            )
        )

        if eligible_license is None:
            raise PlatformUserLicenseNotEligibleError(
                "Platform Administrator bootstrap requires "
                "an eligible issued License."
            )

        if self.platform_user_repository.bootstrap_exists(
            organization.id
        ):
            raise PlatformUserBootstrapAlreadyCompletedError(
                "Platform Administrator bootstrap has already "
                "been completed for this Organization."
            )

        normalized_identity_provider = identity_provider.strip()
        normalized_external_tenant_id = external_tenant_id.strip()
        normalized_external_subject_id = external_subject_id.strip()

        existing_identity = (
            self.platform_user_repository
            .get_by_external_identity(
                organization_id=organization.id,
                identity_provider=normalized_identity_provider,
                external_tenant_id=normalized_external_tenant_id,
                external_subject_id=normalized_external_subject_id,
            )
        )

        if existing_identity is not None:
            raise PlatformUserExternalIdentityConflictError(
                "This external identity is already bound "
                "to a Platform User."
            )

        platform_user = PlatformUser(
            organization_id=organization.id,
            display_name=display_name.strip(),
            email=email.strip().lower(),
            status=PlatformUserStatus.INVITED.value,
            identity_provider=normalized_identity_provider,
            external_tenant_id=normalized_external_tenant_id,
            external_subject_id=normalized_external_subject_id,
            identity_issuer=(
                identity_issuer.strip()
                if identity_issuer
                else None
            ),
            created_via_bootstrap=True,
            invited_at=now,
            activated_at=None,
            last_authenticated_at=None,
            created_by=actor,
            updated_by=actor,
        )

        try:
            platform_user = (
                self.platform_user_repository.create(
                    platform_user
                )
            )

            audit_event = (
                self.audit_service.record_pending(
                    event_type=(
                        "PlatformAdministratorBootstrapped"
                    ),
                    entity_type="PlatformUser",
                    entity_id=platform_user.id,
                    actor=actor,
                    message=(
                        f"Initial Platform Administrator "
                        f"'{platform_user.display_name}' "
                        "was bootstrapped."
                    ),
                    metadata={
                        "organization_id": organization.id,
                        "license_id": eligible_license.id,
                        "license_identifier": (
                            eligible_license
                            .license_identifier
                        ),
                        "platform_user_status": (
                            platform_user.status
                        ),
                        "identity_provider": (
                            platform_user
                            .identity_provider
                        ),
                        "external_tenant_id": (
                            platform_user
                            .external_tenant_id
                        ),
                        "created_via_bootstrap": True,
                        "authorization_granted": (
                            authorization_granted
                        ),
                        "seat_allocated": False,
                        "authentication_completed": False,
                        "actor_trust": (
                            "ServerAssignedSystemActor"
                        ),
                    },
                )
            )

            return (
                platform_user,
                audit_event,
                eligible_license,
            )

        except IntegrityError as error:
            existing_identity = (
                self.platform_user_repository
                .get_by_external_identity(
                    organization_id=organization.id,
                    identity_provider=normalized_identity_provider,
                    external_tenant_id=normalized_external_tenant_id,
                    external_subject_id=normalized_external_subject_id,
                )
            )

            if existing_identity is not None:
                raise PlatformUserExternalIdentityConflictError(
                    "This external identity is already bound "
                    "to a Platform User."
                ) from error

            raise PlatformUserBootstrapAlreadyCompletedError(
                "Platform Administrator bootstrap could not complete "
                "because the Organization changed concurrently."
            ) from error

    @staticmethod
    def _resolve_trusted_lifecycle_actor(
        *,
        organization_id: str,
        trusted_caller: TrustedPlatformCaller,
    ) -> tuple[str, str]:
        """
        Derive immutable audit attribution from trusted caller identity.

        TrustedPlatformCaller carries identity only; HTTP authorization remains
        a separate boundary. This service rejects cross-Organization actor
        context and never accepts free-form actor attribution.
        """

        if trusted_caller is None:
            raise PlatformUserOrganizationBoundaryError(
                "Platform User lifecycle changes require a trusted caller."
            )

        if trusted_caller.organization_id != organization_id:
            raise PlatformUserOrganizationBoundaryError(
                "Trusted Platform caller does not belong to the requested "
                "Organization."
            )

        actor_platform_user_id = str(
            trusted_caller.platform_user_id or ""
        ).strip()

        if not actor_platform_user_id:
            raise PlatformUserOrganizationBoundaryError(
                "Trusted Platform caller is missing Platform User identity."
            )

        return (
            f"{AUTHENTICATED_PLATFORM_USER_ACTOR_PREFIX}"
            f"{actor_platform_user_id}",
            "AuthenticatedPlatformCaller",
        )

    def _require_lifecycle_target(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
    ) -> PlatformUser:
        platform_user = self.platform_user_repository.get_by_id(
            platform_user_id
        )

        if (
            platform_user is None
            or platform_user.organization_id != organization_id
        ):
            raise PlatformUserNotFoundError(
                "Platform User lifecycle target was not found "
                "in the requested Organization."
            )

        return platform_user

    def _another_effective_administrator_exists(
        self,
        *,
        organization_id: str,
        excluded_platform_user_id: str,
        evaluated_at: datetime,
    ) -> bool:
        """
        Reuse the runtime RBAC evaluator as the definition of effective admin.
        """

        for candidate in (
            self.platform_user_repository.list_for_organization(
                organization_id
            )
        ):
            if candidate.id == excluded_platform_user_id:
                continue

            if self.runtime_authorization_service.has_permission(
                organization_id=organization_id,
                platform_user_id=candidate.id,
                permission_key=PLATFORM_ADMINISTRATION_PERMISSION_KEY,
                now=evaluated_at,
            ):
                return True

        return False

    def _protect_last_effective_administrator(
        self,
        *,
        organization_id: str,
        platform_user: PlatformUser,
        evaluated_at: datetime,
    ) -> None:
        """
        Prevent suspension/disablement of the last effective administrator.
        """

        target_is_effective_admin = (
            self.runtime_authorization_service.has_permission(
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                permission_key=PLATFORM_ADMINISTRATION_PERMISSION_KEY,
                now=evaluated_at,
            )
        )

        if not target_is_effective_admin:
            return

        if self._another_effective_administrator_exists(
            organization_id=organization_id,
            excluded_platform_user_id=platform_user.id,
            evaluated_at=evaluated_at,
        ):
            return

        raise PlatformUserLastEffectiveAdministratorError(
            "The last effective Platform administrator cannot be "
            "suspended or disabled."
        )

    def _lifecycle_transition_pending(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        trusted_caller: TrustedPlatformCaller,
        expected_statuses: set[str],
        new_status: str,
        event_type: str,
        action_label: str,
        protect_last_admin: bool,
    ):
        """
        Apply one explicit Platform User lifecycle transition without commit.
        """

        actor, actor_trust = self._resolve_trusted_lifecycle_actor(
            organization_id=organization_id,
            trusted_caller=trusted_caller,
        )

        organization = (
            self.organization_repository
            .get_by_id_for_update(
                organization_id
            )
        )

        if organization is None:
            raise PlatformUserOrganizationNotFoundError(
                "The Platform User lifecycle change references "
                "an unknown Organization."
            )

        platform_user = self._require_lifecycle_target(
            organization_id=organization.id,
            platform_user_id=platform_user_id,
        )

        previous_status = platform_user.status

        if previous_status not in expected_statuses:
            raise PlatformUserInvalidLifecycleTransitionError(
                f"Platform User cannot transition from "
                f"'{previous_status}' to '{new_status}' "
                f"through the {action_label} operation."
            )

        evaluated_at = datetime.now(UTC)

        if protect_last_admin:
            self._protect_last_effective_administrator(
                organization_id=organization.id,
                platform_user=platform_user,
                evaluated_at=evaluated_at,
            )

        original_is_active = platform_user.is_active

        platform_user = (
            self.platform_user_repository
            .set_lifecycle_status(
                platform_user=platform_user,
                status=new_status,
                updated_by=actor,
            )
        )

        if platform_user.is_active != original_is_active:
            raise PlatformUserServiceError(
                "Platform User access lifecycle mutation attempted "
                "to alter record lifecycle state."
            )

        audit_event = self.audit_service.record_pending(
            event_type=event_type,
            entity_type="PlatformUser",
            entity_id=platform_user.id,
            actor=actor,
            message=(
                f"Platform User '{platform_user.display_name}' "
                f"was {action_label}."
            ),
            metadata={
                "organization_id": organization.id,
                "previous_status": previous_status,
                "new_status": new_status,
                "actor_platform_user_id": (
                    trusted_caller.platform_user_id
                ),
                "actor_trust": actor_trust,
                "access_lifecycle_only": True,
                "is_active_preserved": True,
            },
        )

        return platform_user, audit_event

    def suspend(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        trusted_caller: TrustedPlatformCaller,
    ) -> PlatformUser:
        """Suspend one Active Platform User."""

        try:
            platform_user, audit_event = (
                self._lifecycle_transition_pending(
                    organization_id=organization_id,
                    platform_user_id=platform_user_id,
                    trusted_caller=trusted_caller,
                    expected_statuses={
                        PlatformUserStatus.ACTIVE.value,
                    },
                    new_status=PlatformUserStatus.SUSPENDED.value,
                    event_type="PlatformUserSuspended",
                    action_label="suspended",
                    protect_last_admin=True,
                )
            )

            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)

            return platform_user

        except Exception:
            self.db.rollback()
            raise

    def reactivate(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        trusted_caller: TrustedPlatformCaller,
    ) -> PlatformUser:
        """Reactivate one Suspended Platform User."""

        try:
            platform_user, audit_event = (
                self._lifecycle_transition_pending(
                    organization_id=organization_id,
                    platform_user_id=platform_user_id,
                    trusted_caller=trusted_caller,
                    expected_statuses={
                        PlatformUserStatus.SUSPENDED.value,
                    },
                    new_status=PlatformUserStatus.ACTIVE.value,
                    event_type="PlatformUserReactivated",
                    action_label="reactivated",
                    protect_last_admin=False,
                )
            )

            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)

            return platform_user

        except Exception:
            self.db.rollback()
            raise

    def disable(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        trusted_caller: TrustedPlatformCaller,
    ) -> PlatformUser:
        """
        Disable one Invited, Active, or Suspended Platform User.

        Disabled is terminal for V1.
        """

        try:
            platform_user, audit_event = (
                self._lifecycle_transition_pending(
                    organization_id=organization_id,
                    platform_user_id=platform_user_id,
                    trusted_caller=trusted_caller,
                    expected_statuses={
                        PlatformUserStatus.INVITED.value,
                        PlatformUserStatus.ACTIVE.value,
                        PlatformUserStatus.SUSPENDED.value,
                    },
                    new_status=PlatformUserStatus.DISABLED.value,
                    event_type="PlatformUserDisabled",
                    action_label="disabled",
                    protect_last_admin=True,
                )
            )

            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)

            return platform_user

        except Exception:
            self.db.rollback()
            raise

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[PlatformUser]:
        """
        Return Platform Users belonging to one known Organization.

        This read operation does not authenticate the caller, grant
        authorization, allocate Seats, or manage a transaction.
        """

        organization = (
            self.organization_repository.get_by_id(
                organization_id
            )
        )

        if organization is None:
            raise PlatformUserOrganizationNotFoundError(
                "The Platform User query references "
                "an unknown Organization."
            )

        return (
            self.platform_user_repository
            .list_for_organization(
                organization.id
            )
        )

    def get_by_id(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
    ) -> PlatformUser | None:
        """
        Return one Platform User only within the requested Organization.

        A Platform User from another Organization is treated as not found so
        the service does not disclose cross-Organization record existence.
        """

        organization = (
            self.organization_repository.get_by_id(
                organization_id
            )
        )

        if organization is None:
            raise PlatformUserOrganizationNotFoundError(
                "The Platform User query references "
                "an unknown Organization."
            )

        platform_user = (
            self.platform_user_repository.get_by_id(
                platform_user_id
            )
        )

        if (
            platform_user is None
            or platform_user.organization_id
            != organization.id
        ):
            return None

        return platform_user

    def bootstrap_first_administrator(
        self,
        *,
        organization_id: str,
        display_name: str,
        email: str,
        identity_provider: str,
        external_tenant_id: str,
        external_subject_id: str,
        identity_issuer: str | None = None,
        actor: str = SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
        evaluated_at: datetime | None = None,
    ) -> PlatformUser:
        """
        Create the first Platform User for one eligible Organization.

        The public operation owns its standalone database transaction.
        """

        try:
            (
                platform_user,
                audit_event,
                _eligible_license,
            ) = self._bootstrap_first_administrator_pending(
                organization_id=organization_id,
                display_name=display_name,
                email=email,
                identity_provider=identity_provider,
                external_tenant_id=external_tenant_id,
                external_subject_id=external_subject_id,
                identity_issuer=identity_issuer,
                actor=actor,
                evaluated_at=evaluated_at,
                authorization_granted=False,
            )

            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)

            return platform_user

        except Exception:
            self.db.rollback()
            raise
