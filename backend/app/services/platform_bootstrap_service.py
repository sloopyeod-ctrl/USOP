from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.platform_role_status import PlatformRoleStatus
from app.models.platform_permission import PlatformPermission
from app.models.platform_role import PlatformRole
from app.repositories.platform_permission_repository import (
    PlatformPermissionRepository,
)
from app.repositories.platform_role_repository import (
    PlatformRoleRepository,
)
from app.schemas.platform_bootstrap import PlatformBootstrapResult
from app.services.audit_service import AuditService
from app.services.platform_authorization_service import (
    PlatformAuthorizationService,
)
from app.services.platform_user_service import PlatformUserService


SYSTEM_PLATFORM_BOOTSTRAP_ACTOR = (
    "USOP Platform Bootstrap Service"
)

PLATFORM_ADMINISTRATOR_ROLE_KEY = (
    "platform-administrator"
)

PLATFORM_ADMINISTRATION_PERMISSION_KEY = (
    "platform-administration.manage"
)

PLATFORM_ADMINISTRATION_RESOURCE = (
    "platform-administration"
)

PLATFORM_ADMINISTRATION_ACTION = (
    "manage"
)


class PlatformBootstrapServiceError(ValueError):
    """
    Base failure raised by PlatformBootstrapService.
    """


class PlatformBootstrapConflictError(
    PlatformBootstrapServiceError
):
    """
    Raised when existing authorization vocabulary conflicts
    with canonical Platform bootstrap values.
    """


class PlatformBootstrapService:
    """
    Atomic initial Platform Administrator orchestration.

    This service coordinates identity bootstrap and authorization
    establishment inside one caller-owned database transaction.
    """

    def __init__(self, db: Session):
        self.db = db

        self.platform_user_service = (
            PlatformUserService(db)
        )

        self.platform_authorization_service = (
            PlatformAuthorizationService(db)
        )

        self.platform_role_repository = (
            PlatformRoleRepository(db)
        )

        self.platform_permission_repository = (
            PlatformPermissionRepository(db)
        )

        self.audit_service = AuditService(db)

    def _resolve_or_create_platform_administrator_role(
        self,
        *,
        organization_id: str,
    ):
        """
        Resolve or create the canonical Organization-scoped
        Platform Administrator system role.
        """

        platform_role = (
            self.platform_role_repository.get_by_key(
                organization_id=organization_id,
                role_key=PLATFORM_ADMINISTRATOR_ROLE_KEY,
            )
        )

        if platform_role is not None:
            if (
                platform_role.status
                != PlatformRoleStatus.ACTIVE.value
            ):
                raise PlatformBootstrapConflictError(
                    "The canonical Platform Administrator role "
                    "exists but is not active."
                )

            if platform_role.is_system_role is not True:
                raise PlatformBootstrapConflictError(
                    "The canonical Platform Administrator role "
                    "exists but is not marked as a system role."
                )

            return platform_role, None

        platform_role = PlatformRole(
            organization_id=organization_id,
            role_key=PLATFORM_ADMINISTRATOR_ROLE_KEY,
            name="Platform Administrator",
            description=(
                "Canonical system role assigned to the first "
                "administrator of a USOP Organization."
            ),
            status=PlatformRoleStatus.ACTIVE.value,
            is_system_role=True,
            created_by=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
            updated_by=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
        )

        try:
            platform_role = (
                self.platform_role_repository.create(
                    platform_role
                )
            )
        except IntegrityError as error:
            raise PlatformBootstrapConflictError(
                "The canonical Platform Administrator role "
                "could not be created because a conflicting "
                "role already exists."
            ) from error

        audit_event = self.audit_service.record_pending(
            event_type="PlatformRoleCreated",
            entity_type="PlatformRole",
            entity_id=platform_role.id,
            actor=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
            message=(
                "Canonical Platform Administrator system role "
                "was created during bootstrap."
            ),
            metadata={
                "organization_id": organization_id,
                "platform_role_id": platform_role.id,
                "platform_role_key": platform_role.role_key,
                "platform_role_status": platform_role.status,
                "is_system_role": (
                    platform_role.is_system_role
                ),
                "actor_trust": (
                    "ServerAssignedSystemActor"
                ),
            },
        )

        return platform_role, audit_event

    def _resolve_or_create_platform_administration_permission(
        self,
    ):
        """
        Resolve or create the canonical global Platform
        administration permission.
        """

        platform_permission = (
            self.platform_permission_repository.get_by_key(
                PLATFORM_ADMINISTRATION_PERMISSION_KEY
            )
        )

        if platform_permission is not None:
            if (
                platform_permission.resource
                != PLATFORM_ADMINISTRATION_RESOURCE
            ):
                raise PlatformBootstrapConflictError(
                    "The canonical Platform administration "
                    "permission exists with a conflicting resource."
                )

            if (
                platform_permission.action
                != PLATFORM_ADMINISTRATION_ACTION
            ):
                raise PlatformBootstrapConflictError(
                    "The canonical Platform administration "
                    "permission exists with a conflicting action."
                )

            if (
                platform_permission.is_system_permission
                is not True
            ):
                raise PlatformBootstrapConflictError(
                    "The canonical Platform administration "
                    "permission is not marked as a system permission."
                )

            return platform_permission, None

        existing_resource_action = (
            self.platform_permission_repository
            .get_by_resource_action(
                resource=PLATFORM_ADMINISTRATION_RESOURCE,
                action=PLATFORM_ADMINISTRATION_ACTION,
            )
        )

        if existing_resource_action is not None:
            raise PlatformBootstrapConflictError(
                "A Platform Permission already exists for the "
                "canonical administration resource and action "
                "with a different permission key."
            )

        platform_permission = PlatformPermission(
            permission_key=(
                PLATFORM_ADMINISTRATION_PERMISSION_KEY
            ),
            name="Manage Platform Administration",
            description=(
                "Manage Platform Users, authorization, and "
                "administrative settings within USOP."
            ),
            resource=PLATFORM_ADMINISTRATION_RESOURCE,
            action=PLATFORM_ADMINISTRATION_ACTION,
            is_system_permission=True,
            created_by=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
            updated_by=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
        )

        try:
            platform_permission = (
                self.platform_permission_repository.create(
                    platform_permission
                )
            )
        except IntegrityError as error:
            raise PlatformBootstrapConflictError(
                "The canonical Platform administration "
                "permission could not be created because a "
                "conflicting permission already exists."
            ) from error

        audit_event = self.audit_service.record_pending(
            event_type="PlatformPermissionCreated",
            entity_type="PlatformPermission",
            entity_id=platform_permission.id,
            actor=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
            message=(
                "Canonical Platform administration permission "
                "was created during bootstrap."
            ),
            metadata={
                "platform_permission_id": (
                    platform_permission.id
                ),
                "permission_key": (
                    platform_permission.permission_key
                ),
                "resource": platform_permission.resource,
                "action": platform_permission.action,
                "is_system_permission": (
                    platform_permission.is_system_permission
                ),
                "actor_trust": (
                    "ServerAssignedSystemActor"
                ),
            },
        )

        return platform_permission, audit_event

    def bootstrap_platform_administrator(
        self,
        *,
        organization_id: str,
        display_name: str,
        email: str,
        identity_provider: str,
        external_tenant_id: str,
        external_subject_id: str,
        identity_issuer: str | None = None,
        evaluated_at: datetime | None = None,
    ) -> PlatformBootstrapResult:
        """
        Create the first Platform Administrator and its authority
        atomically with exactly one database commit.
        """

        effective_time = (
            evaluated_at or datetime.now(UTC)
        )

        try:
            (
                platform_user,
                user_audit_event,
                eligible_license,
            ) = (
                self.platform_user_service
                ._bootstrap_first_administrator_pending(
                    organization_id=organization_id,
                    display_name=display_name,
                    email=email,
                    identity_provider=identity_provider,
                    external_tenant_id=external_tenant_id,
                    external_subject_id=external_subject_id,
                    identity_issuer=identity_issuer,
                    actor=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
                    evaluated_at=effective_time,
                    authorization_granted=True,
                )
            )

            (
                platform_role,
                role_audit_event,
            ) = (
                self
                ._resolve_or_create_platform_administrator_role(
                    organization_id=organization_id,
                )
            )

            (
                platform_permission,
                permission_audit_event,
            ) = (
                self
                ._resolve_or_create_platform_administration_permission()
            )

            (
                role_permission_mapping,
                mapping_audit_event,
            ) = (
                self.platform_authorization_service
                ._grant_permission_pending(
                    organization_id=organization_id,
                    platform_role_id=platform_role.id,
                    platform_permission_id=(
                        platform_permission.id
                    ),
                )
            )

            (
                role_assignment,
                assignment_audit_event,
            ) = (
                self.platform_authorization_service
                ._assign_role_pending(
                    organization_id=organization_id,
                    platform_user_id=platform_user.id,
                    platform_role_id=platform_role.id,
                    assigned_at=effective_time,
                )
            )

            completion_audit_event = (
                self.audit_service.record_pending(
                    event_type=(
                        "PlatformBootstrapCompleted"
                    ),
                    entity_type="Organization",
                    entity_id=organization_id,
                    actor=SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
                    message=(
                        "Initial Platform Administrator identity "
                        "and authorization were created atomically."
                    ),
                    metadata={
                        "organization_id": organization_id,
                        "license_id": eligible_license.id,
                        "platform_user_id": (
                            platform_user.id
                        ),
                        "platform_role_id": (
                            platform_role.id
                        ),
                        "platform_permission_id": (
                            platform_permission.id
                        ),
                        "role_permission_mapping_id": (
                            role_permission_mapping.id
                        ),
                        "role_assignment_id": (
                            role_assignment.id
                        ),
                        "authorization_granted": True,
                        "seat_allocated": False,
                        "authentication_completed": False,
                        "actor_trust": (
                            "ServerAssignedSystemActor"
                        ),
                    },
                )
            )

            self.db.commit()

            refreshable_records = [
                platform_user,
                platform_role,
                platform_permission,
                role_permission_mapping,
                role_assignment,
                user_audit_event,
                mapping_audit_event,
                assignment_audit_event,
                completion_audit_event,
            ]

            if role_audit_event is not None:
                refreshable_records.append(
                    role_audit_event
                )

            if permission_audit_event is not None:
                refreshable_records.append(
                    permission_audit_event
                )

            for record in refreshable_records:
                self.db.refresh(record)

            audit_event_ids = [
                user_audit_event.id,
            ]

            if role_audit_event is not None:
                audit_event_ids.append(
                    role_audit_event.id
                )

            if permission_audit_event is not None:
                audit_event_ids.append(
                    permission_audit_event.id
                )

            audit_event_ids.extend(
                [
                    mapping_audit_event.id,
                    assignment_audit_event.id,
                    completion_audit_event.id,
                ]
            )

            return PlatformBootstrapResult(
                organization_id=organization_id,
                license_id=eligible_license.id,
                platform_user_id=platform_user.id,
                platform_role_id=platform_role.id,
                platform_permission_id=(
                    platform_permission.id
                ),
                role_permission_mapping_id=(
                    role_permission_mapping.id
                ),
                role_assignment_id=role_assignment.id,
                audit_event_ids=audit_event_ids,
                platform_user_status=(
                    platform_user.status
                ),
                role_key=platform_role.role_key,
                permission_key=(
                    platform_permission.permission_key
                ),
                authorization_granted=True,
                seat_allocated=False,
                authentication_completed=False,
            )

        except IntegrityError as error:
            self.db.rollback()

            raise PlatformBootstrapConflictError(
                "Platform Administrator bootstrap could not "
                "complete because a conflicting record changed "
                "concurrently."
            ) from error

        except Exception:
            self.db.rollback()
            raise
