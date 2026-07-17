import inspect
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.domain.organization_status import OrganizationStatus
from app.domain.platform_role_status import PlatformRoleStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.models.audit_event import AuditEvent
from app.models.organization import Organization
from app.models.platform_permission import PlatformPermission
from app.models.platform_role import PlatformRole
from app.models.platform_role_assignment import (
    PlatformRoleAssignment,
)
from app.models.platform_role_permission import (
    PlatformRolePermission,
)
from app.models.platform_user import PlatformUser
from app.services.platform_authorization_service import (
    SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
    PlatformAuthorizationAssignmentConflictError,
    PlatformAuthorizationAssignmentNotFoundError,
    PlatformAuthorizationAssignmentWindowError,
    PlatformAuthorizationMappingConflictError,
    PlatformAuthorizationMappingNotFoundError,
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationOrganizationNotActiveError,
    PlatformAuthorizationOrganizationNotFoundError,
    PlatformAuthorizationPermissionNotFoundError,
    PlatformAuthorizationRoleNotActiveError,
    PlatformAuthorizationRoleNotFoundError,
    PlatformAuthorizationService,
    PlatformAuthorizationUserNotAssignableError,
    PlatformAuthorizationUserNotFoundError,
)


ACTOR = "USOP Platform Authorization Service Regression"


def build_organization(
    *,
    suffix: str,
    label: str,
    status: OrganizationStatus = OrganizationStatus.ACTIVE,
) -> Organization:
    return Organization(
        name=f"Authorization Service {label}",
        slug=f"authorization-service-{label.lower()}-{suffix}",
        status=status.value,
        organization_type="Customer",
        time_zone="UTC",
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def build_user(
    *,
    organization_id: str,
    suffix: str,
    label: str,
    status: PlatformUserStatus,
    now: datetime,
) -> PlatformUser:
    return PlatformUser(
        organization_id=organization_id,
        display_name=f"{label} Platform User",
        email=f"{label.lower()}-{suffix}@example.invalid",
        status=status.value,
        identity_provider="MicrosoftEntraID",
        external_tenant_id=str(uuid.uuid4()),
        external_subject_id=str(uuid.uuid4()),
        created_via_bootstrap=(
            status == PlatformUserStatus.INVITED
        ),
        invited_at=now,
        activated_at=(
            now
            if status == PlatformUserStatus.ACTIVE
            else None
        ),
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def build_role(
    *,
    organization_id: str,
    role_key: str,
    name: str,
    status: PlatformRoleStatus,
) -> PlatformRole:
    return PlatformRole(
        organization_id=organization_id,
        role_key=role_key,
        name=name,
        description=f"{name} regression role.",
        status=status.value,
        is_system_role=True,
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def build_permission(
    *,
    suffix: str,
    key_name: str,
    resource: str,
    action: str,
) -> PlatformPermission:
    return PlatformPermission(
        permission_key=f"{key_name}.{suffix}",
        name=key_name.replace("-", " ").title(),
        description=f"{key_name} regression permission.",
        resource=resource,
        action=f"{action}-{suffix}",
        is_system_permission=True,
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def main() -> int:
    print("USOP Platform Authorization Service Regression")
    print("----------------------------------------------")

    db = SessionLocal()
    service = PlatformAuthorizationService(db)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_ids: list[str] = []
    permission_ids: list[str] = []
    errors: list[str] = []

    try:
        primary = build_organization(
            suffix=suffix,
            label="Primary",
        )

        secondary = build_organization(
            suffix=suffix,
            label="Secondary",
        )

        suspended_organization = build_organization(
            suffix=suffix,
            label="Suspended",
            status=OrganizationStatus.SUSPENDED,
        )

        db.add_all(
            [
                primary,
                secondary,
                suspended_organization,
            ]
        )
        db.commit()

        for organization in (
            primary,
            secondary,
            suspended_organization,
        ):
            db.refresh(organization)
            organization_ids.append(organization.id)

        invited_user = build_user(
            organization_id=primary.id,
            suffix=suffix,
            label="Invited",
            status=PlatformUserStatus.INVITED,
            now=now,
        )

        active_user = build_user(
            organization_id=primary.id,
            suffix=suffix,
            label="Active",
            status=PlatformUserStatus.ACTIVE,
            now=now,
        )

        suspended_user = build_user(
            organization_id=primary.id,
            suffix=suffix,
            label="Suspended",
            status=PlatformUserStatus.SUSPENDED,
            now=now,
        )

        disabled_user = build_user(
            organization_id=primary.id,
            suffix=suffix,
            label="Disabled",
            status=PlatformUserStatus.DISABLED,
            now=now,
        )

        secondary_user = build_user(
            organization_id=secondary.id,
            suffix=suffix,
            label="Secondary",
            status=PlatformUserStatus.ACTIVE,
            now=now,
        )

        active_role = build_role(
            organization_id=primary.id,
            role_key="platform-administrator",
            name="Platform Administrator",
            status=PlatformRoleStatus.ACTIVE,
        )

        secondary_active_role = build_role(
            organization_id=primary.id,
            role_key="security-administrator",
            name="Security Administrator",
            status=PlatformRoleStatus.ACTIVE,
        )

        disabled_role = build_role(
            organization_id=primary.id,
            role_key="disabled-role",
            name="Disabled Role",
            status=PlatformRoleStatus.DISABLED,
        )

        foreign_role = build_role(
            organization_id=secondary.id,
            role_key="foreign-administrator",
            name="Foreign Administrator",
            status=PlatformRoleStatus.ACTIVE,
        )

        read_permission = build_permission(
            suffix=suffix,
            key_name="platform-users-read",
            resource="platform-users",
            action="read",
        )

        manage_permission = build_permission(
            suffix=suffix,
            key_name="platform-users-manage",
            resource="platform-users",
            action="manage",
        )

        rollback_permission = build_permission(
            suffix=suffix,
            key_name="platform-users-rollback",
            resource="platform-users",
            action="rollback",
        )

        db.add_all(
            [
                invited_user,
                active_user,
                suspended_user,
                disabled_user,
                secondary_user,
                active_role,
                secondary_active_role,
                disabled_role,
                foreign_role,
                read_permission,
                manage_permission,
                rollback_permission,
            ]
        )
        db.commit()

        for record in (
            invited_user,
            active_user,
            suspended_user,
            disabled_user,
            secondary_user,
            active_role,
            secondary_active_role,
            disabled_role,
            foreign_role,
            read_permission,
            manage_permission,
            rollback_permission,
        ):
            db.refresh(record)

        permission_ids.extend(
            [
                read_permission.id,
                manage_permission.id,
                rollback_permission.id,
            ]
        )

        unknown_organization_rejected = False

        try:
            service.assign_role(
                organization_id=str(uuid.uuid4()),
                platform_user_id=invited_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationOrganizationNotFoundError:
            unknown_organization_rejected = True

        if not unknown_organization_rejected:
            errors.append(
                "Unknown Organization was accepted."
            )

        suspended_organization_rejected = False

        try:
            service.assign_role(
                organization_id=suspended_organization.id,
                platform_user_id=invited_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationOrganizationNotActiveError:
            suspended_organization_rejected = True

        if not suspended_organization_rejected:
            errors.append(
                "Suspended Organization was accepted."
            )

        unknown_user_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=str(uuid.uuid4()),
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationUserNotFoundError:
            unknown_user_rejected = True

        if not unknown_user_rejected:
            errors.append(
                "Unknown Platform User was accepted."
            )

        unknown_role_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=invited_user.id,
                platform_role_id=str(uuid.uuid4()),
                assigned_at=now,
            )
        except PlatformAuthorizationRoleNotFoundError:
            unknown_role_rejected = True

        if not unknown_role_rejected:
            errors.append(
                "Unknown Platform Role was accepted."
            )

        cross_organization_user_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=secondary_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationOrganizationBoundaryError:
            cross_organization_user_rejected = True

        if not cross_organization_user_rejected:
            errors.append(
                "Cross-Organization Platform User assignment was accepted."
            )

        cross_organization_role_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=invited_user.id,
                platform_role_id=foreign_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationOrganizationBoundaryError:
            cross_organization_role_rejected = True

        if not cross_organization_role_rejected:
            errors.append(
                "Cross-Organization Platform Role assignment was accepted."
            )

        suspended_user_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=suspended_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationUserNotAssignableError:
            suspended_user_rejected = True

        if not suspended_user_rejected:
            errors.append(
                "Suspended Platform User received new authority."
            )

        disabled_user_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=disabled_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationUserNotAssignableError:
            disabled_user_rejected = True

        if not disabled_user_rejected:
            errors.append(
                "Disabled Platform User received new authority."
            )

        disabled_role_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=invited_user.id,
                platform_role_id=disabled_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationRoleNotActiveError:
            disabled_role_rejected = True

        if not disabled_role_rejected:
            errors.append(
                "Disabled Platform Role was assigned."
            )

        invalid_window_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=invited_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
                expires_at=now,
            )
        except PlatformAuthorizationAssignmentWindowError:
            invalid_window_rejected = True

        if not invalid_window_rejected:
            errors.append(
                "Invalid assignment time window was accepted."
            )

        invited_assignment = service.assign_role(
            organization_id=primary.id,
            platform_user_id=invited_user.id,
            platform_role_id=active_role.id,
            assigned_at=now,
            expires_at=now + timedelta(days=30),
        )

        persisted_invited_assignment = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.id
                == invited_assignment.id
            )
            .one_or_none()
        )

        if persisted_invited_assignment is None:
            errors.append(
                "Invited Platform User assignment was not persisted."
            )

        duplicate_assignment_rejected = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=invited_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except PlatformAuthorizationAssignmentConflictError:
            duplicate_assignment_rejected = True

        if not duplicate_assignment_rejected:
            errors.append(
                "Duplicate Platform Role assignment was accepted."
            )

        active_assignment = service.assign_role(
            organization_id=primary.id,
            platform_user_id=active_user.id,
            platform_role_id=secondary_active_role.id,
            assigned_at=now,
        )

        assignment_audits = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.event_type
                == "PlatformRoleAssigned",
                AuditEvent.entity_type
                == "PlatformRoleAssignment",
                AuditEvent.entity_id.in_(
                    [
                        invited_assignment.id,
                        active_assignment.id,
                    ]
                ),
            )
            .all()
        )

        if len(assignment_audits) != 2:
            errors.append(
                "Valid assignments did not create exactly two audit events."
            )

        assignment_actor_controlled = all(
            event.actor
            == SYSTEM_PLATFORM_AUTHORIZATION_ACTOR
            for event in assignment_audits
        )

        if not assignment_actor_controlled:
            errors.append(
                "Assignment actor attribution was not server-controlled."
            )

        unknown_permission_rejected = False

        try:
            service.grant_permission(
                organization_id=primary.id,
                platform_role_id=active_role.id,
                platform_permission_id=str(uuid.uuid4()),
            )
        except PlatformAuthorizationPermissionNotFoundError:
            unknown_permission_rejected = True

        if not unknown_permission_rejected:
            errors.append(
                "Unknown Platform Permission was accepted."
            )

        cross_organization_mapping_rejected = False

        try:
            service.grant_permission(
                organization_id=secondary.id,
                platform_role_id=active_role.id,
                platform_permission_id=read_permission.id,
            )
        except PlatformAuthorizationOrganizationBoundaryError:
            cross_organization_mapping_rejected = True

        if not cross_organization_mapping_rejected:
            errors.append(
                "Cross-Organization role-permission mapping was accepted."
            )

        disabled_role_mapping_rejected = False

        try:
            service.grant_permission(
                organization_id=primary.id,
                platform_role_id=disabled_role.id,
                platform_permission_id=read_permission.id,
            )
        except PlatformAuthorizationRoleNotActiveError:
            disabled_role_mapping_rejected = True

        if not disabled_role_mapping_rejected:
            errors.append(
                "Disabled Platform Role received a new permission."
            )

        read_mapping = service.grant_permission(
            organization_id=primary.id,
            platform_role_id=active_role.id,
            platform_permission_id=read_permission.id,
        )

        persisted_read_mapping = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.id == read_mapping.id
            )
            .one_or_none()
        )

        if persisted_read_mapping is None:
            errors.append(
                "Platform Permission mapping was not persisted."
            )

        duplicate_mapping_rejected = False

        try:
            service.grant_permission(
                organization_id=primary.id,
                platform_role_id=active_role.id,
                platform_permission_id=read_permission.id,
            )
        except PlatformAuthorizationMappingConflictError:
            duplicate_mapping_rejected = True

        if not duplicate_mapping_rejected:
            errors.append(
                "Duplicate Platform Permission mapping was accepted."
            )

        manage_mapping = service.grant_permission(
            organization_id=primary.id,
            platform_role_id=active_role.id,
            platform_permission_id=manage_permission.id,
        )

        mapping_audits = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.event_type
                == "PlatformPermissionGranted",
                AuditEvent.entity_type
                == "PlatformRolePermission",
                AuditEvent.entity_id.in_(
                    [
                        read_mapping.id,
                        manage_mapping.id,
                    ]
                ),
            )
            .all()
        )

        if len(mapping_audits) != 2:
            errors.append(
                "Valid permission grants did not create two audit events."
            )

        original_record_pending = (
            service.audit_service.record_pending
        )

        def fail_assignment_audit(**kwargs):
            raise RuntimeError(
                "Simulated assignment audit failure."
            )

        service.audit_service.record_pending = (
            fail_assignment_audit
        )

        assignment_rollback_triggered = False

        try:
            service.assign_role(
                organization_id=primary.id,
                platform_user_id=active_user.id,
                platform_role_id=active_role.id,
                assigned_at=now,
            )
        except RuntimeError:
            assignment_rollback_triggered = True
        finally:
            service.audit_service.record_pending = (
                original_record_pending
            )

        rolled_back_assignment_count = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == primary.id,
                PlatformRoleAssignment.platform_user_id
                == active_user.id,
                PlatformRoleAssignment.platform_role_id
                == active_role.id,
            )
            .count()
        )

        if not assignment_rollback_triggered:
            errors.append(
                "Assignment audit failure did not propagate."
            )

        if rolled_back_assignment_count != 0:
            errors.append(
                "Assignment remained after audit failure rollback."
            )

        def fail_mapping_audit(**kwargs):
            raise RuntimeError(
                "Simulated mapping audit failure."
            )

        service.audit_service.record_pending = (
            fail_mapping_audit
        )

        mapping_rollback_triggered = False

        try:
            service.grant_permission(
                organization_id=primary.id,
                platform_role_id=secondary_active_role.id,
                platform_permission_id=rollback_permission.id,
            )
        except RuntimeError:
            mapping_rollback_triggered = True
        finally:
            service.audit_service.record_pending = (
                original_record_pending
            )

        rolled_back_mapping_count = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == primary.id,
                PlatformRolePermission.platform_role_id
                == secondary_active_role.id,
                PlatformRolePermission.platform_permission_id
                == rollback_permission.id,
            )
            .count()
        )

        if not mapping_rollback_triggered:
            errors.append(
                "Permission grant audit failure did not propagate."
            )

        if rolled_back_mapping_count != 0:
            errors.append(
                "Permission mapping remained after audit failure rollback."
            )

        service.remove_role(
            organization_id=primary.id,
            platform_user_id=active_user.id,
            platform_role_id=secondary_active_role.id,
        )

        removed_assignment_count = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.id
                == active_assignment.id
            )
            .count()
        )

        if removed_assignment_count != 0:
            errors.append(
                "Platform Role assignment was not removed."
            )

        missing_assignment_rejected = False

        try:
            service.remove_role(
                organization_id=primary.id,
                platform_user_id=active_user.id,
                platform_role_id=secondary_active_role.id,
            )
        except PlatformAuthorizationAssignmentNotFoundError:
            missing_assignment_rejected = True

        if not missing_assignment_rejected:
            errors.append(
                "Missing Platform Role assignment removal was accepted."
            )

        service.remove_permission(
            organization_id=primary.id,
            platform_role_id=active_role.id,
            platform_permission_id=manage_permission.id,
        )

        removed_mapping_count = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.id
                == manage_mapping.id
            )
            .count()
        )

        if removed_mapping_count != 0:
            errors.append(
                "Platform Permission mapping was not removed."
            )

        missing_mapping_rejected = False

        try:
            service.remove_permission(
                organization_id=primary.id,
                platform_role_id=active_role.id,
                platform_permission_id=manage_permission.id,
            )
        except PlatformAuthorizationMappingNotFoundError:
            missing_mapping_rejected = True

        if not missing_mapping_rejected:
            errors.append(
                "Missing Platform Permission removal was accepted."
            )

        removal_audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.event_type.in_(
                    [
                        "PlatformRoleRemoved",
                        "PlatformPermissionRemoved",
                    ]
                )
            )
            .filter(
                AuditEvent.metadata_json["organization_id"]
                .as_string()
                == primary.id
            )
            .count()
        )

        if removal_audit_count != 2:
            errors.append(
                "Authority removals did not create exactly two audit events."
            )

        public_methods = {
            "assign_role": service.assign_role,
            "remove_role": service.remove_role,
            "grant_permission": service.grant_permission,
            "remove_permission": service.remove_permission,
        }

        browser_actor_parameter_exposed = any(
            "actor" in inspect.signature(method).parameters
            for method in public_methods.values()
        )

        if browser_actor_parameter_exposed:
            errors.append(
                "Authorization service exposes caller-controlled actor input."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Primary Organization ID: {primary.id}")
        print(f"Secondary Organization ID: {secondary.id}")
        print(f"Invited assignment ID: {invited_assignment.id}")
        print(f"Read permission mapping ID: {read_mapping.id}")
        print(
            "Unknown Organization rejected: "
            f"{unknown_organization_rejected}"
        )
        print(
            "Suspended Organization rejected: "
            f"{suspended_organization_rejected}"
        )
        print(
            "Unknown Platform User rejected: "
            f"{unknown_user_rejected}"
        )
        print(
            "Unknown Platform Role rejected: "
            f"{unknown_role_rejected}"
        )
        print(
            "Cross-Organization user rejected: "
            f"{cross_organization_user_rejected}"
        )
        print(
            "Cross-Organization role rejected: "
            f"{cross_organization_role_rejected}"
        )
        print(
            "Suspended Platform User rejected: "
            f"{suspended_user_rejected}"
        )
        print(
            "Disabled Platform User rejected: "
            f"{disabled_user_rejected}"
        )
        print(
            "Disabled Platform Role rejected: "
            f"{disabled_role_rejected}"
        )
        print(
            "Invalid assignment window rejected: "
            f"{invalid_window_rejected}"
        )
        print(
            "Invited Platform User assignable: "
            f"{persisted_invited_assignment is not None}"
        )
        print(
            "Active Platform User assignable: True"
        )
        print(
            "Duplicate assignment rejected: "
            f"{duplicate_assignment_rejected}"
        )
        print(
            "Unknown Platform Permission rejected: "
            f"{unknown_permission_rejected}"
        )
        print(
            "Cross-Organization mapping rejected: "
            f"{cross_organization_mapping_rejected}"
        )
        print(
            "Disabled role permission grant rejected: "
            f"{disabled_role_mapping_rejected}"
        )
        print(
            "Duplicate permission mapping rejected: "
            f"{duplicate_mapping_rejected}"
        )
        print(
            "Assignment audit failure rolled back: "
            f"{rolled_back_assignment_count == 0}"
        )
        print(
            "Permission audit failure rolled back: "
            f"{rolled_back_mapping_count == 0}"
        )
        print(
            "Role assignment removal persisted: "
            f"{removed_assignment_count == 0}"
        )
        print(
            "Permission removal persisted: "
            f"{removed_mapping_count == 0}"
        )
        print(
            "Missing assignment removal rejected: "
            f"{missing_assignment_rejected}"
        )
        print(
            "Missing permission removal rejected: "
            f"{missing_mapping_rejected}"
        )
        print(
            "Server-controlled actor attribution: "
            f"{assignment_actor_controlled}"
        )
        print(
            "Browser-controlled actor parameter exposed: "
            f"{browser_actor_parameter_exposed}"
        )

        print()
        print("Validation: PASSED")
        print(
            "PlatformAuthorizationService is the atomic security boundary "
            "for Platform Role assignments and permission mappings. It "
            "enforces Organization consistency, lifecycle policy, duplicate "
            "prevention, server-controlled attribution, immutable auditing, "
            "and rollback on failed authorization changes."
        )

        return 0

    finally:
        db.rollback()

        if organization_ids:
            role_ids = [
                item[0]
                for item in (
                    db.query(PlatformRole.id)
                    .filter(
                        PlatformRole.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            user_ids = [
                item[0]
                for item in (
                    db.query(PlatformUser.id)
                    .filter(
                        PlatformUser.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            assignment_ids = [
                item[0]
                for item in (
                    db.query(PlatformRoleAssignment.id)
                    .filter(
                        PlatformRoleAssignment.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            mapping_ids = [
                item[0]
                for item in (
                    db.query(PlatformRolePermission.id)
                    .filter(
                        PlatformRolePermission.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            audit_entity_ids = (
                assignment_ids
                + mapping_ids
            )

            if audit_entity_ids:
                (
                    db.query(AuditEvent)
                    .filter(
                        AuditEvent.entity_id.in_(
                            audit_entity_ids
                        )
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            (
                db.query(PlatformRoleAssignment)
                .filter(
                    PlatformRoleAssignment.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            if role_ids:
                (
                    db.query(PlatformRolePermission)
                    .filter(
                        PlatformRolePermission.platform_role_id.in_(
                            role_ids
                        )
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            (
                db.query(PlatformRole)
                .filter(
                    PlatformRole.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            if user_ids:
                (
                    db.query(PlatformUser)
                    .filter(
                        PlatformUser.id.in_(user_ids)
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            if permission_ids:
                (
                    db.query(PlatformPermission)
                    .filter(
                        PlatformPermission.id.in_(
                            permission_ids
                        )
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            (
                db.query(Organization)
                .filter(
                    Organization.id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
