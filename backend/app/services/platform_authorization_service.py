from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.organization_status import OrganizationStatus
from app.domain.platform_role_status import PlatformRoleStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.models.platform_permission import PlatformPermission
from app.models.platform_role import PlatformRole
from app.models.platform_role_assignment import (
    PlatformRoleAssignment,
)
from app.models.platform_role_permission import (
    PlatformRolePermission,
)
from app.models.platform_user import PlatformUser
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.platform_permission_repository import (
    PlatformPermissionRepository,
)
from app.repositories.platform_role_assignment_repository import (
    PlatformRoleAssignmentRepository,
)
from app.repositories.platform_role_permission_repository import (
    PlatformRolePermissionRepository,
)
from app.repositories.platform_role_repository import (
    PlatformRoleRepository,
)
from app.repositories.platform_user_repository import (
    PlatformUserRepository,
)
from app.services.audit_service import AuditService


SYSTEM_PLATFORM_AUTHORIZATION_ACTOR = (
    "USOP Platform Authorization Service"
)

ASSIGNABLE_PLATFORM_USER_STATUSES = {
    PlatformUserStatus.INVITED.value,
    PlatformUserStatus.ACTIVE.value,
}


class PlatformAuthorizationServiceError(ValueError):
    """Base exception for Platform authorization service failures."""


class PlatformAuthorizationOrganizationNotFoundError(
    PlatformAuthorizationServiceError
):
    """Raised when an unknown Organization is referenced."""


class PlatformAuthorizationOrganizationNotActiveError(
    PlatformAuthorizationServiceError
):
    """Raised when authority is changed for a non-active Organization."""


class PlatformAuthorizationUserNotFoundError(
    PlatformAuthorizationServiceError
):
    """Raised when an unknown Platform User is referenced."""


class PlatformAuthorizationUserNotAssignableError(
    PlatformAuthorizationServiceError
):
    """Raised when a Platform User cannot receive new authority."""


class PlatformAuthorizationRoleNotFoundError(
    PlatformAuthorizationServiceError
):
    """Raised when an unknown Platform Role is referenced."""


class PlatformAuthorizationRoleNotActiveError(
    PlatformAuthorizationServiceError
):
    """Raised when a disabled Platform Role is assigned or expanded."""


class PlatformAuthorizationPermissionNotFoundError(
    PlatformAuthorizationServiceError
):
    """Raised when an unknown Platform Permission is referenced."""


class PlatformAuthorizationOrganizationBoundaryError(
    PlatformAuthorizationServiceError
):
    """Raised when referenced records cross an Organization boundary."""


class PlatformAuthorizationAssignmentConflictError(
    PlatformAuthorizationServiceError
):
    """Raised when a Platform Role assignment already exists."""


class PlatformAuthorizationAssignmentNotFoundError(
    PlatformAuthorizationServiceError
):
    """Raised when a Platform Role assignment does not exist."""


class PlatformAuthorizationMappingConflictError(
    PlatformAuthorizationServiceError
):
    """Raised when a Platform Role already has a permission."""


class PlatformAuthorizationMappingNotFoundError(
    PlatformAuthorizationServiceError
):
    """Raised when a Platform Role permission mapping does not exist."""


class PlatformAuthorizationAssignmentWindowError(
    PlatformAuthorizationServiceError
):
    """Raised when an assignment expiration is not after assignment time."""


class PlatformAuthorizationService:
    """
    Security and transaction boundary for USOP Platform authorization.

    Only this service may create or remove PlatformRoleAssignment and
    PlatformRolePermission records.

    Repositories provide persistence only. This service owns:

    - Organization lifecycle validation
    - Cross-record Organization consistency
    - Platform User assignment eligibility
    - Platform Role lifecycle validation
    - Duplicate prevention
    - Immutable audit creation
    - Atomic commit and rollback

    Actor attribution is server-controlled. Public methods intentionally do
    not accept an actor supplied by an API request or browser.
    """

    def __init__(self, db: Session):
        self.db = db
        self.organization_repository = OrganizationRepository(db)
        self.platform_user_repository = PlatformUserRepository(db)
        self.platform_role_repository = PlatformRoleRepository(db)
        self.platform_permission_repository = (
            PlatformPermissionRepository(db)
        )
        self.assignment_repository = (
            PlatformRoleAssignmentRepository(db)
        )
        self.mapping_repository = (
            PlatformRolePermissionRepository(db)
        )
        self.audit_service = AuditService(db)

    def _require_active_organization(
        self,
        organization_id: str,
    ):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise PlatformAuthorizationOrganizationNotFoundError(
                "Platform authorization references an unknown Organization."
            )

        if organization.status != OrganizationStatus.ACTIVE.value:
            raise PlatformAuthorizationOrganizationNotActiveError(
                "Platform authorization changes require an active "
                "Organization."
            )

        return organization

    def _require_platform_user(
        self,
        platform_user_id: str,
    ) -> PlatformUser:
        platform_user = self.platform_user_repository.get_by_id(
            platform_user_id
        )

        if platform_user is None:
            raise PlatformAuthorizationUserNotFoundError(
                "Platform authorization references an unknown Platform User."
            )

        return platform_user

    def _require_platform_role(
        self,
        platform_role_id: str,
    ) -> PlatformRole:
        platform_role = self.platform_role_repository.get_by_id(
            platform_role_id
        )

        if platform_role is None:
            raise PlatformAuthorizationRoleNotFoundError(
                "Platform authorization references an unknown Platform Role."
            )

        return platform_role

    def _require_platform_permission(
        self,
        platform_permission_id: str,
    ) -> PlatformPermission:
        platform_permission = (
            self.platform_permission_repository.get_by_id(
                platform_permission_id
            )
        )

        if platform_permission is None:
            raise PlatformAuthorizationPermissionNotFoundError(
                "Platform authorization references an unknown "
                "Platform Permission."
            )

        return platform_permission

    @staticmethod
    def _validate_user_organization(
        *,
        organization_id: str,
        platform_user: PlatformUser,
    ) -> None:
        if platform_user.organization_id != organization_id:
            raise PlatformAuthorizationOrganizationBoundaryError(
                "The Platform User does not belong to the requested "
                "Organization."
            )

    @staticmethod
    def _validate_role_organization(
        *,
        organization_id: str,
        platform_role: PlatformRole,
    ) -> None:
        if platform_role.organization_id != organization_id:
            raise PlatformAuthorizationOrganizationBoundaryError(
                "The Platform Role does not belong to the requested "
                "Organization."
            )

    @staticmethod
    def _validate_user_assignable(
        platform_user: PlatformUser,
    ) -> None:
        if (
            platform_user.status
            not in ASSIGNABLE_PLATFORM_USER_STATUSES
        ):
            raise PlatformAuthorizationUserNotAssignableError(
                "Platform Roles may be assigned only to Invited or "
                "Active Platform Users."
            )

    @staticmethod
    def _validate_role_active(
        platform_role: PlatformRole,
    ) -> None:
        if platform_role.status != PlatformRoleStatus.ACTIVE.value:
            raise PlatformAuthorizationRoleNotActiveError(
                "Platform authority may be assigned only through an "
                "active Platform Role."
            )

    @staticmethod
    def _validate_assignment_window(
        *,
        assigned_at: datetime,
        expires_at: datetime | None,
    ) -> None:
        if expires_at is None:
            return

        normalized_assigned_at = (
            assigned_at.replace(tzinfo=UTC)
            if assigned_at.tzinfo is None
            else assigned_at
        )

        normalized_expires_at = (
            expires_at.replace(tzinfo=UTC)
            if expires_at.tzinfo is None
            else expires_at
        )

        if normalized_expires_at <= normalized_assigned_at:
            raise PlatformAuthorizationAssignmentWindowError(
                "Platform Role assignment expiration must be after "
                "the assignment time."
            )

    def assign_role(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        platform_role_id: str,
        expires_at: datetime | None = None,
        assigned_at: datetime | None = None,
    ) -> PlatformRoleAssignment:
        """
        Assign one active Platform Role to an eligible Platform User.

        Invited users are eligible so the initial bootstrap administrator may
        receive authority before completing first authentication. Suspended
        and Disabled users cannot receive new authority.
        """

        organization = self._require_active_organization(
            organization_id
        )

        platform_user = self._require_platform_user(
            platform_user_id
        )

        platform_role = self._require_platform_role(
            platform_role_id
        )

        self._validate_user_organization(
            organization_id=organization.id,
            platform_user=platform_user,
        )

        self._validate_role_organization(
            organization_id=organization.id,
            platform_role=platform_role,
        )

        self._validate_user_assignable(platform_user)
        self._validate_role_active(platform_role)

        effective_assigned_at = (
            assigned_at or datetime.now(UTC)
        )

        self._validate_assignment_window(
            assigned_at=effective_assigned_at,
            expires_at=expires_at,
        )

        existing = self.assignment_repository.get_assignment(
            organization_id=organization.id,
            platform_user_id=platform_user.id,
            platform_role_id=platform_role.id,
        )

        if existing is not None:
            raise PlatformAuthorizationAssignmentConflictError(
                "This Platform Role is already assigned to the "
                "Platform User."
            )

        assignment = PlatformRoleAssignment(
            organization_id=organization.id,
            platform_user_id=platform_user.id,
            platform_role_id=platform_role.id,
            assigned_at=effective_assigned_at,
            expires_at=expires_at,
            created_by=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
            updated_by=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
        )

        try:
            assignment = self.assignment_repository.create(
                assignment
            )

            audit_event = self.audit_service.record_pending(
                event_type="PlatformRoleAssigned",
                entity_type="PlatformRoleAssignment",
                entity_id=assignment.id,
                actor=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
                message=(
                    f"Platform Role '{platform_role.name}' was assigned "
                    f"to Platform User '{platform_user.display_name}'."
                ),
                metadata={
                    "organization_id": organization.id,
                    "platform_user_id": platform_user.id,
                    "platform_user_status": platform_user.status,
                    "platform_role_id": platform_role.id,
                    "platform_role_key": platform_role.role_key,
                    "platform_role_status": platform_role.status,
                    "assigned_at": (
                        assignment.assigned_at.isoformat()
                    ),
                    "expires_at": (
                        assignment.expires_at.isoformat()
                        if assignment.expires_at
                        else None
                    ),
                    "actor_trust": "ServerAssignedSystemActor",
                },
            )

            self.db.commit()
            self.db.refresh(assignment)
            self.db.refresh(audit_event)

            return assignment

        except IntegrityError as error:
            self.db.rollback()

            raise PlatformAuthorizationAssignmentConflictError(
                "The Platform Role assignment could not be created "
                "because an equivalent assignment already exists."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def remove_role(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        platform_role_id: str,
    ) -> None:
        """
        Remove one Platform Role assignment.

        Revocation remains available even when the Platform User is suspended
        or the Platform Role is disabled. This prevents lifecycle state from
        blocking removal of existing authority.
        """

        organization = self._require_active_organization(
            organization_id
        )

        platform_user = self._require_platform_user(
            platform_user_id
        )

        platform_role = self._require_platform_role(
            platform_role_id
        )

        self._validate_user_organization(
            organization_id=organization.id,
            platform_user=platform_user,
        )

        self._validate_role_organization(
            organization_id=organization.id,
            platform_role=platform_role,
        )

        assignment = self.assignment_repository.get_assignment(
            organization_id=organization.id,
            platform_user_id=platform_user.id,
            platform_role_id=platform_role.id,
        )

        if assignment is None:
            raise PlatformAuthorizationAssignmentNotFoundError(
                "The requested Platform Role assignment does not exist."
            )

        assignment_id = assignment.id

        try:
            self.db.delete(assignment)
            self.db.flush()

            audit_event = self.audit_service.record_pending(
                event_type="PlatformRoleRemoved",
                entity_type="PlatformRoleAssignment",
                entity_id=assignment_id,
                actor=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
                message=(
                    f"Platform Role '{platform_role.name}' was removed "
                    f"from Platform User '{platform_user.display_name}'."
                ),
                metadata={
                    "organization_id": organization.id,
                    "platform_user_id": platform_user.id,
                    "platform_user_status": platform_user.status,
                    "platform_role_id": platform_role.id,
                    "platform_role_key": platform_role.role_key,
                    "platform_role_status": platform_role.status,
                    "actor_trust": "ServerAssignedSystemActor",
                },
            )

            self.db.commit()
            self.db.refresh(audit_event)

        except Exception:
            self.db.rollback()
            raise

    def grant_permission(
        self,
        *,
        organization_id: str,
        platform_role_id: str,
        platform_permission_id: str,
    ) -> PlatformRolePermission:
        """
        Grant one global Platform Permission to an active Organization role.
        """

        organization = self._require_active_organization(
            organization_id
        )

        platform_role = self._require_platform_role(
            platform_role_id
        )

        platform_permission = self._require_platform_permission(
            platform_permission_id
        )

        self._validate_role_organization(
            organization_id=organization.id,
            platform_role=platform_role,
        )

        self._validate_role_active(platform_role)

        existing = self.mapping_repository.get_mapping(
            organization_id=organization.id,
            platform_role_id=platform_role.id,
            platform_permission_id=platform_permission.id,
        )

        if existing is not None:
            raise PlatformAuthorizationMappingConflictError(
                "This Platform Permission is already granted to the "
                "Platform Role."
            )

        mapping = PlatformRolePermission(
            organization_id=organization.id,
            platform_role_id=platform_role.id,
            platform_permission_id=platform_permission.id,
            created_by=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
            updated_by=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
        )

        try:
            mapping = self.mapping_repository.create(mapping)

            audit_event = self.audit_service.record_pending(
                event_type="PlatformPermissionGranted",
                entity_type="PlatformRolePermission",
                entity_id=mapping.id,
                actor=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
                message=(
                    f"Platform Permission "
                    f"'{platform_permission.permission_key}' was granted "
                    f"to Platform Role '{platform_role.name}'."
                ),
                metadata={
                    "organization_id": organization.id,
                    "platform_role_id": platform_role.id,
                    "platform_role_key": platform_role.role_key,
                    "platform_role_status": platform_role.status,
                    "platform_permission_id": platform_permission.id,
                    "permission_key": (
                        platform_permission.permission_key
                    ),
                    "resource": platform_permission.resource,
                    "action": platform_permission.action,
                    "actor_trust": "ServerAssignedSystemActor",
                },
            )

            self.db.commit()
            self.db.refresh(mapping)
            self.db.refresh(audit_event)

            return mapping

        except IntegrityError as error:
            self.db.rollback()

            raise PlatformAuthorizationMappingConflictError(
                "The Platform Permission grant could not be created "
                "because an equivalent mapping already exists."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def remove_permission(
        self,
        *,
        organization_id: str,
        platform_role_id: str,
        platform_permission_id: str,
    ) -> None:
        """
        Remove one Platform Permission from a Platform Role.

        Revocation remains available when the Platform Role is disabled.
        """

        organization = self._require_active_organization(
            organization_id
        )

        platform_role = self._require_platform_role(
            platform_role_id
        )

        platform_permission = self._require_platform_permission(
            platform_permission_id
        )

        self._validate_role_organization(
            organization_id=organization.id,
            platform_role=platform_role,
        )

        mapping = self.mapping_repository.get_mapping(
            organization_id=organization.id,
            platform_role_id=platform_role.id,
            platform_permission_id=platform_permission.id,
        )

        if mapping is None:
            raise PlatformAuthorizationMappingNotFoundError(
                "The requested Platform Role permission mapping "
                "does not exist."
            )

        mapping_id = mapping.id

        try:
            self.db.delete(mapping)
            self.db.flush()

            audit_event = self.audit_service.record_pending(
                event_type="PlatformPermissionRemoved",
                entity_type="PlatformRolePermission",
                entity_id=mapping_id,
                actor=SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
                message=(
                    f"Platform Permission "
                    f"'{platform_permission.permission_key}' was removed "
                    f"from Platform Role '{platform_role.name}'."
                ),
                metadata={
                    "organization_id": organization.id,
                    "platform_role_id": platform_role.id,
                    "platform_role_key": platform_role.role_key,
                    "platform_role_status": platform_role.status,
                    "platform_permission_id": platform_permission.id,
                    "permission_key": (
                        platform_permission.permission_key
                    ),
                    "resource": platform_permission.resource,
                    "action": platform_permission.action,
                    "actor_trust": "ServerAssignedSystemActor",
                },
            )

            self.db.commit()
            self.db.refresh(audit_event)

        except Exception:
            self.db.rollback()
            raise
