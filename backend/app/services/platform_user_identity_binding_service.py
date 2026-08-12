from sqlalchemy.orm import Session

from app.models.platform_user import PlatformUser
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.organizational_identity_repository import (
    OrganizationalIdentityRepository,
)
from app.repositories.platform_user_repository import PlatformUserRepository
from app.services.audit_service import AuditService


class PlatformUserIdentityBindingServiceError(ValueError):
    """Base exception for Platform User identity-binding failures."""


class PlatformUserIdentityBindingOrganizationNotFoundError(
    PlatformUserIdentityBindingServiceError
):
    """Raised when the requested Organization does not exist."""


class PlatformUserIdentityBindingPlatformUserNotFoundError(
    PlatformUserIdentityBindingServiceError
):
    """Raised when the Platform User is not visible in the Organization."""


class PlatformUserIdentityBindingOrganizationalIdentityNotFoundError(
    PlatformUserIdentityBindingServiceError
):
    """Raised without disclosing whether a foreign-tenant record exists."""


class PlatformUserIdentityBindingActorRequiredError(
    PlatformUserIdentityBindingServiceError
):
    """Raised when an audited mutation has no explicit actor."""


class PlatformUserIdentityBindingService:
    """
    Authoritative binding boundary between USOP operators and identity context.

    PlatformUser remains the control-plane principal. OrganizationalIdentity
    remains the Organization-owned representation of canonical identity.

    This service connects the concepts without merging them.
    """

    def __init__(
        self,
        db: Session,
        *,
        organization_repository: OrganizationRepository | None = None,
        platform_user_repository: PlatformUserRepository | None = None,
        organizational_identity_repository: (
            OrganizationalIdentityRepository | None
        ) = None,
        audit_service: AuditService | None = None,
    ):
        self.db = db
        self.organization_repository = (
            organization_repository or OrganizationRepository(db)
        )
        self.platform_user_repository = (
            platform_user_repository or PlatformUserRepository(db)
        )
        self.organizational_identity_repository = (
            organizational_identity_repository
            or OrganizationalIdentityRepository(db)
        )
        self.audit_service = audit_service or AuditService(db)

    @staticmethod
    def _normalize_required(value: str, *, field_name: str) -> str:
        normalized = (value or "").strip()
        if not normalized:
            raise PlatformUserIdentityBindingServiceError(
                f"{field_name} is required."
            )
        return normalized

    @staticmethod
    def _require_actor(actor: str) -> str:
        normalized = (actor or "").strip()
        if not normalized:
            raise PlatformUserIdentityBindingActorRequiredError(
                "Platform User identity binding requires an explicit audit actor."
            )
        return normalized

    def _resolve_platform_user(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
    ) -> PlatformUser:
        organization = self.organization_repository.get_by_id(organization_id)
        if organization is None:
            raise PlatformUserIdentityBindingOrganizationNotFoundError(
                "The Platform User identity binding references "
                "an unknown Organization."
            )

        platform_user = self.platform_user_repository.get_by_id(platform_user_id)
        if (
            platform_user is None
            or platform_user.organization_id != organization.id
        ):
            raise PlatformUserIdentityBindingPlatformUserNotFoundError(
                "Platform User not found in the requested Organization."
            )

        return platform_user

    def bind(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        organizational_identity_id: str,
        actor: str,
    ) -> PlatformUser:
        organization_id = self._normalize_required(
            organization_id,
            field_name="organization_id",
        )
        platform_user_id = self._normalize_required(
            platform_user_id,
            field_name="platform_user_id",
        )
        organizational_identity_id = self._normalize_required(
            organizational_identity_id,
            field_name="organizational_identity_id",
        )
        actor = self._require_actor(actor)

        platform_user = self._resolve_platform_user(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
        )

        organizational_identity = (
            self.organizational_identity_repository.get_by_id_for_organization(
                organization_id=organization_id,
                organizational_identity_id=organizational_identity_id,
            )
        )
        if organizational_identity is None:
            raise PlatformUserIdentityBindingOrganizationalIdentityNotFoundError(
                "Organizational Identity not found in the requested Organization."
            )

        if (
            platform_user.organizational_identity_id
            == organizational_identity.id
        ):
            return platform_user

        previous_id = platform_user.organizational_identity_id

        try:
            platform_user.updated_by = actor
            platform_user = (
                self.platform_user_repository
                .set_organizational_identity_binding(
                    platform_user=platform_user,
                    organizational_identity_id=organizational_identity.id,
                )
            )
            audit_event = self.audit_service.record_pending(
                event_type="PlatformUserIdentityBound",
                entity_type="PlatformUser",
                entity_id=platform_user.id,
                actor=actor,
                message=(
                    f"Platform User '{platform_user.display_name}' "
                    "was bound to an Organizational Identity."
                ),
                metadata={
                    "organization_id": organization_id,
                    "platform_user_id": platform_user.id,
                    "previous_organizational_identity_id": previous_id,
                    "organizational_identity_id": organizational_identity.id,
                    "identity_id": organizational_identity.identity_id,
                    "binding_authority": "ExplicitServerSideMutation",
                    "correlation_method": "ExplicitBinding",
                },
            )
            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)
            return platform_user
        except Exception:
            self.db.rollback()
            raise

    def unbind(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        actor: str,
    ) -> PlatformUser:
        organization_id = self._normalize_required(
            organization_id,
            field_name="organization_id",
        )
        platform_user_id = self._normalize_required(
            platform_user_id,
            field_name="platform_user_id",
        )
        actor = self._require_actor(actor)

        platform_user = self._resolve_platform_user(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
        )
        previous_id = platform_user.organizational_identity_id

        if previous_id is None:
            return platform_user

        try:
            platform_user.updated_by = actor
            platform_user = (
                self.platform_user_repository
                .set_organizational_identity_binding(
                    platform_user=platform_user,
                    organizational_identity_id=None,
                )
            )
            audit_event = self.audit_service.record_pending(
                event_type="PlatformUserIdentityUnbound",
                entity_type="PlatformUser",
                entity_id=platform_user.id,
                actor=actor,
                message=(
                    f"Platform User '{platform_user.display_name}' "
                    "was unbound from its Organizational Identity."
                ),
                metadata={
                    "organization_id": organization_id,
                    "platform_user_id": platform_user.id,
                    "previous_organizational_identity_id": previous_id,
                    "organizational_identity_id": None,
                    "binding_authority": "ExplicitServerSideMutation",
                },
            )
            self.db.commit()
            self.db.refresh(platform_user)
            self.db.refresh(audit_event)
            return platform_user
        except Exception:
            self.db.rollback()
            raise
