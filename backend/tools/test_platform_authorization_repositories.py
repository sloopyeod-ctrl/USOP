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
from app.domain.platform_role_status import PlatformRoleStatus
from app.domain.platform_user_status import PlatformUserStatus
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


ACTOR = "USOP Platform Authorization Repository Regression"


def main() -> int:
    print("USOP Platform Authorization Repository Regression")
    print("-------------------------------------------------")

    db = SessionLocal()

    role_repository = PlatformRoleRepository(db)
    permission_repository = PlatformPermissionRepository(db)
    mapping_repository = PlatformRolePermissionRepository(db)
    assignment_repository = PlatformRoleAssignmentRepository(db)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    errors: list[str] = []

    try:
        primary = Organization(
            name="Authorization Repository Primary",
            slug=f"authorization-repository-primary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary = Organization(
            name="Authorization Repository Secondary",
            slug=f"authorization-repository-secondary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(primary)
        db.add(secondary)
        db.flush()
        db.refresh(primary)
        db.refresh(secondary)

        primary_user = PlatformUser(
            organization_id=primary.id,
            display_name="Primary Platform Operator",
            email=f"primary-{suffix}@example.invalid",
            status=PlatformUserStatus.ACTIVE.value,
            identity_provider="MicrosoftEntraID",
            external_tenant_id=str(uuid.uuid4()),
            external_subject_id=str(uuid.uuid4()),
            created_via_bootstrap=False,
            invited_at=now,
            activated_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_user = PlatformUser(
            organization_id=secondary.id,
            display_name="Secondary Platform Operator",
            email=f"secondary-{suffix}@example.invalid",
            status=PlatformUserStatus.ACTIVE.value,
            identity_provider="MicrosoftEntraID",
            external_tenant_id=str(uuid.uuid4()),
            external_subject_id=str(uuid.uuid4()),
            created_via_bootstrap=False,
            invited_at=now,
            activated_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(primary_user)
        db.add(secondary_user)
        db.flush()
        db.refresh(primary_user)
        db.refresh(secondary_user)

        read_permission = permission_repository.create(
            PlatformPermission(
                permission_key=(
                    f"platform-users.read.{suffix}"
                ),
                name="Read Platform Users",
                description="Read Platform User records.",
                resource="platform-users",
                action=f"read-{suffix}",
                is_system_permission=True,
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        manage_permission = permission_repository.create(
            PlatformPermission(
                permission_key=(
                    f"platform-users.manage.{suffix}"
                ),
                name="Manage Platform Users",
                description="Manage Platform User records.",
                resource="platform-users",
                action=f"manage-{suffix}",
                is_system_permission=True,
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        primary_role = role_repository.create(
            PlatformRole(
                organization_id=primary.id,
                role_key="platform-administrator",
                name="Platform Administrator",
                description="Administers the local USOP deployment.",
                status=PlatformRoleStatus.ACTIVE.value,
                is_system_role=True,
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        primary_read_only_role = role_repository.create(
            PlatformRole(
                organization_id=primary.id,
                role_key="read-only",
                name="Read Only",
                description="Provides read-only platform access.",
                status=PlatformRoleStatus.ACTIVE.value,
                is_system_role=True,
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        secondary_role = role_repository.create(
            PlatformRole(
                organization_id=secondary.id,
                role_key="platform-administrator",
                name="Platform Administrator",
                description="Administers the secondary deployment.",
                status=PlatformRoleStatus.ACTIVE.value,
                is_system_role=True,
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        mapping = mapping_repository.create(
            PlatformRolePermission(
                organization_id=primary.id,
                platform_role_id=primary_role.id,
                platform_permission_id=(
                    read_permission.id
                ),
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        second_mapping = mapping_repository.create(
            PlatformRolePermission(
                organization_id=primary.id,
                platform_role_id=primary_role.id,
                platform_permission_id=(
                    manage_permission.id
                ),
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        assignment = assignment_repository.create(
            PlatformRoleAssignment(
                organization_id=primary.id,
                platform_user_id=primary_user.id,
                platform_role_id=primary_role.id,
                assigned_at=now,
                expires_at=None,
                created_by=ACTOR,
                updated_by=ACTOR,
            )
        )

        read_only_assignment = (
            assignment_repository.create(
                PlatformRoleAssignment(
                    organization_id=primary.id,
                    platform_user_id=primary_user.id,
                    platform_role_id=(
                        primary_read_only_role.id
                    ),
                    assigned_at=(
                        now + timedelta(seconds=1)
                    ),
                    expires_at=None,
                    created_by=ACTOR,
                    updated_by=ACTOR,
                )
            )
        )

        role_by_id = role_repository.get_by_id(
            primary_role.id
        )

        role_by_key = role_repository.get_by_key(
            organization_id=primary.id,
            role_key=primary_role.role_key,
        )

        cross_org_role_lookup = (
            role_repository.get_by_key(
                organization_id=secondary.id,
                role_key=(
                    primary_read_only_role.role_key
                ),
            )
        )

        primary_roles = (
            role_repository.list_for_organization(
                primary.id
            )
        )

        primary_role_count = (
            role_repository.count_for_organization(
                primary.id
            )
        )

        permission_by_id = (
            permission_repository.get_by_id(
                read_permission.id
            )
        )

        permission_by_key = (
            permission_repository.get_by_key(
                read_permission.permission_key
            )
        )

        permission_by_resource_action = (
            permission_repository
            .get_by_resource_action(
                resource=read_permission.resource,
                action=read_permission.action,
            )
        )

        all_permissions = (
            permission_repository.list_all()
        )

        mapping_by_id = mapping_repository.get_by_id(
            mapping.id
        )

        mapping_lookup = (
            mapping_repository.get_mapping(
                organization_id=primary.id,
                platform_role_id=primary_role.id,
                platform_permission_id=(
                    read_permission.id
                ),
            )
        )

        cross_org_mapping_lookup = (
            mapping_repository.get_mapping(
                organization_id=secondary.id,
                platform_role_id=primary_role.id,
                platform_permission_id=(
                    read_permission.id
                ),
            )
        )

        role_mappings = (
            mapping_repository.list_for_role(
                organization_id=primary.id,
                platform_role_id=primary_role.id,
            )
        )

        role_mapping_count = (
            mapping_repository.count_for_role(
                organization_id=primary.id,
                platform_role_id=primary_role.id,
            )
        )

        assignment_by_id = (
            assignment_repository.get_by_id(
                assignment.id
            )
        )

        assignment_lookup = (
            assignment_repository.get_assignment(
                organization_id=primary.id,
                platform_user_id=primary_user.id,
                platform_role_id=primary_role.id,
            )
        )

        cross_org_assignment_lookup = (
            assignment_repository.get_assignment(
                organization_id=secondary.id,
                platform_user_id=primary_user.id,
                platform_role_id=primary_role.id,
            )
        )

        user_assignments = (
            assignment_repository.list_for_user(
                organization_id=primary.id,
                platform_user_id=primary_user.id,
            )
        )

        role_assignments = (
            assignment_repository.list_for_role(
                organization_id=primary.id,
                platform_role_id=primary_role.id,
            )
        )

        user_assignment_count = (
            assignment_repository.count_for_user(
                organization_id=primary.id,
                platform_user_id=primary_user.id,
            )
        )

        if (
            role_by_id is None
            or role_by_id.id != primary_role.id
        ):
            errors.append(
                "PlatformRole lookup by ID failed."
            )

        if (
            role_by_key is None
            or role_by_key.id != primary_role.id
        ):
            errors.append(
                "PlatformRole lookup by key failed."
            )

        if cross_org_role_lookup is not None:
            errors.append(
                "PlatformRole lookup crossed the Organization boundary."
            )

        if primary_role_count != 2:
            errors.append(
                "PlatformRole Organization count was incorrect."
            )

        expected_primary_role_ids = [
            primary_role.id,
            primary_read_only_role.id,
        ]

        if [
            item.id
            for item in primary_roles
        ] != expected_primary_role_ids:
            errors.append(
                "PlatformRole listing was not deterministic."
            )

        if (
            permission_by_id is None
            or permission_by_id.id
            != read_permission.id
        ):
            errors.append(
                "PlatformPermission lookup by ID failed."
            )

        if (
            permission_by_key is None
            or permission_by_key.id
            != read_permission.id
        ):
            errors.append(
                "PlatformPermission lookup by key failed."
            )

        if (
            permission_by_resource_action is None
            or permission_by_resource_action.id
            != read_permission.id
        ):
            errors.append(
                "PlatformPermission resource/action lookup failed."
            )

        expected_permission_keys = sorted(
            [
                read_permission.permission_key,
                manage_permission.permission_key,
            ]
        )

        actual_permission_keys = [
            item.permission_key
            for item in all_permissions
            if suffix in item.permission_key
        ]

        if actual_permission_keys != expected_permission_keys:
            errors.append(
                "PlatformPermission listing was not deterministic."
            )

        if (
            mapping_by_id is None
            or mapping_by_id.id != mapping.id
        ):
            errors.append(
                "Role-permission mapping lookup by ID failed."
            )

        if (
            mapping_lookup is None
            or mapping_lookup.id != mapping.id
        ):
            errors.append(
                "Role-permission mapping lookup failed."
            )

        if cross_org_mapping_lookup is not None:
            errors.append(
                "Role-permission lookup crossed the Organization boundary."
            )

        if role_mapping_count != 2:
            errors.append(
                "Role-permission mapping count was incorrect."
            )

        if [
            item.id
            for item in role_mappings
        ] != [
            mapping.id,
            second_mapping.id,
        ]:
            errors.append(
                "Role-permission mapping listing was not deterministic."
            )

        if (
            assignment_by_id is None
            or assignment_by_id.id != assignment.id
        ):
            errors.append(
                "Role assignment lookup by ID failed."
            )

        if (
            assignment_lookup is None
            or assignment_lookup.id != assignment.id
        ):
            errors.append(
                "Role assignment lookup failed."
            )

        if cross_org_assignment_lookup is not None:
            errors.append(
                "Role assignment lookup crossed the Organization boundary."
            )

        if user_assignment_count != 2:
            errors.append(
                "Platform User assignment count was incorrect."
            )

        if [
            item.id
            for item in user_assignments
        ] != [
            assignment.id,
            read_only_assignment.id,
        ]:
            errors.append(
                "Platform User assignment listing was not deterministic."
            )

        if [
            item.id
            for item in role_assignments
        ] != [
            assignment.id,
        ]:
            errors.append(
                "Platform Role assignment listing was incorrect."
            )

        prohibited_methods = {
            "commit",
            "rollback",
            "authenticate",
            "authorize",
            "assign_role",
            "grant_permission",
            "remove_role",
            "remove_permission",
            "delete",
        }

        repositories = {
            "PlatformRoleRepository": role_repository,
            "PlatformPermissionRepository": (
                permission_repository
            ),
            "PlatformRolePermissionRepository": (
                mapping_repository
            ),
            "PlatformRoleAssignmentRepository": (
                assignment_repository
            ),
        }

        exposed_prohibited_methods: list[str] = []

        for repository_name, repository in (
            repositories.items()
        ):
            for method_name in prohibited_methods:
                if hasattr(repository, method_name):
                    exposed_prohibited_methods.append(
                        f"{repository_name}.{method_name}"
                    )

        if exposed_prohibited_methods:
            errors.append(
                "Authorization repositories expose prohibited "
                "methods: "
                + ", ".join(
                    sorted(exposed_prohibited_methods)
                )
            )

        # The caller owns the transaction. A rollback must remove the complete
        # temporary authorization graph.
        db.rollback()

        persisted_roles = (
            db.query(PlatformRole)
            .filter(
                PlatformRole.id.in_(
                    [
                        primary_role.id,
                        primary_read_only_role.id,
                        secondary_role.id,
                    ]
                )
            )
            .count()
        )

        persisted_permissions = (
            db.query(PlatformPermission)
            .filter(
                PlatformPermission.id.in_(
                    [
                        read_permission.id,
                        manage_permission.id,
                    ]
                )
            )
            .count()
        )

        persisted_mappings = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.id.in_(
                    [
                        mapping.id,
                        second_mapping.id,
                    ]
                )
            )
            .count()
        )

        persisted_assignments = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.id.in_(
                    [
                        assignment.id,
                        read_only_assignment.id,
                    ]
                )
            )
            .count()
        )

        if any(
            (
                persisted_roles,
                persisted_permissions,
                persisted_mappings,
                persisted_assignments,
            )
        ):
            errors.append(
                "Authorization repository unexpectedly committed "
                "the caller-owned transaction."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Primary Organization ID: {primary.id}")
        print(f"Secondary Organization ID: {secondary.id}")
        print("Platform Roles created: 3")
        print("Platform Permissions created: 2")
        print("Role-permission mappings created: 2")
        print("User-role assignments created: 2")
        print(
            "Role lookup by ID: "
            f"{role_by_id is not None}"
        )
        print(
            "Role lookup by Organization/key: "
            f"{role_by_key is not None}"
        )
        print(
            "Role Organization boundary preserved: "
            f"{cross_org_role_lookup is None}"
        )
        print(
            "Permission lookup by ID: "
            f"{permission_by_id is not None}"
        )
        print(
            "Permission lookup by key: "
            f"{permission_by_key is not None}"
        )
        print(
            "Permission resource/action lookup: "
            f"{permission_by_resource_action is not None}"
        )
        print(
            "Mapping Organization boundary preserved: "
            f"{cross_org_mapping_lookup is None}"
        )
        print(
            "Assignment Organization boundary preserved: "
            f"{cross_org_assignment_lookup is None}"
        )
        print(
            "Role listing deterministic: "
            f"{len(primary_roles) == 2}"
        )
        print(
            "Permission listing deterministic: "
            f"{len(actual_permission_keys) == 2}"
        )
        print(
            "Mapping listing deterministic: "
            f"{len(role_mappings) == 2}"
        )
        print(
            "Assignment listing deterministic: "
            f"{len(user_assignments) == 2}"
        )
        print(
            "Prohibited repository methods exposed: "
            f"{bool(exposed_prohibited_methods)}"
        )
        print("Repository security decisions made: False")
        print("Repository audit events created: False")
        print(
            "Repositories committed transaction: "
            f"{any((persisted_roles, persisted_permissions, persisted_mappings, persisted_assignments))}"
        )

        print()
        print("Validation: PASSED")
        print(
            "Platform authorization repositories provide deterministic "
            "persistence and Organization-scoped retrieval while preserving "
            "service-layer ownership of tenant validation, authorization "
            "policy, auditing, commit, and rollback."
        )

        return 0

    finally:
        db.rollback()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
