import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError


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


ACTOR = "USOP Platform Authorization Persistence Regression"


def main() -> int:
    print("USOP Platform Authorization Persistence Regression")
    print("--------------------------------------------------")

    db = SessionLocal()

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_ids: list[str] = []
    errors: list[str] = []

    try:
        primary = Organization(
            name="Authorization Persistence Primary",
            slug=f"authorization-primary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary = Organization(
            name="Authorization Persistence Secondary",
            slug=f"authorization-secondary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(primary)
        db.add(secondary)
        db.commit()
        db.refresh(primary)
        db.refresh(secondary)

        organization_ids.extend(
            [
                primary.id,
                secondary.id,
            ]
        )

        primary_user = PlatformUser(
            organization_id=primary.id,
            display_name="Primary Platform User",
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
            display_name="Secondary Platform User",
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
        db.commit()
        db.refresh(primary_user)
        db.refresh(secondary_user)

        permission = PlatformPermission(
            permission_key=f"platform-users.read.{suffix}",
            name="Read Platform Users",
            description=(
                "Read Platform User records in the Administration Workspace."
            ),
            resource="platform-users",
            action=f"read-{suffix}",
            is_system_permission=True,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

        primary_role = PlatformRole(
            organization_id=primary.id,
            role_key="platform-administrator",
            name="Platform Administrator",
            description="Administers the customer-local USOP platform.",
            status=PlatformRoleStatus.ACTIVE.value,
            is_system_role=True,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_role = PlatformRole(
            organization_id=secondary.id,
            role_key="platform-administrator",
            name="Platform Administrator",
            description="Administers the customer-local USOP platform.",
            status=PlatformRoleStatus.ACTIVE.value,
            is_system_role=True,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(primary_role)
        db.add(secondary_role)
        db.commit()
        db.refresh(primary_role)
        db.refresh(secondary_role)

        mapping = PlatformRolePermission(
            organization_id=primary.id,
            platform_role_id=primary_role.id,
            platform_permission_id=permission.id,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        assignment = PlatformRoleAssignment(
            organization_id=primary.id,
            platform_user_id=primary_user.id,
            platform_role_id=primary_role.id,
            assigned_at=now,
            expires_at=now + timedelta(days=30),
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(mapping)
        db.add(assignment)
        db.commit()
        db.refresh(mapping)
        db.refresh(assignment)

        persisted_mapping = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.id == mapping.id
            )
            .one_or_none()
        )

        persisted_assignment = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.id == assignment.id
            )
            .one_or_none()
        )

        if persisted_mapping is None:
            errors.append(
                "PlatformRolePermission was not persisted."
            )

        if persisted_assignment is None:
            errors.append(
                "PlatformRoleAssignment was not persisted."
            )

        duplicate_role_rejected = False

        duplicate_role = PlatformRole(
            organization_id=primary.id,
            role_key=primary_role.role_key,
            name="Duplicate Platform Administrator",
            status=PlatformRoleStatus.ACTIVE.value,
            is_system_role=False,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(duplicate_role)

        try:
            db.commit()
        except IntegrityError:
            duplicate_role_rejected = True
            db.rollback()

        if not duplicate_role_rejected:
            errors.append(
                "Duplicate Organization-scoped role key was accepted."
            )

        duplicate_permission_key_rejected = False

        duplicate_permission_key = PlatformPermission(
            permission_key=permission.permission_key,
            name="Duplicate Permission Key",
            resource=f"different-resource-{suffix}",
            action=f"different-action-{suffix}",
            is_system_permission=False,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(duplicate_permission_key)

        try:
            db.commit()
        except IntegrityError:
            duplicate_permission_key_rejected = True
            db.rollback()

        if not duplicate_permission_key_rejected:
            errors.append(
                "Duplicate Platform permission key was accepted."
            )

        duplicate_resource_action_rejected = False

        duplicate_resource_action = PlatformPermission(
            permission_key=f"different-key-{suffix}",
            name="Duplicate Resource Action",
            resource=permission.resource,
            action=permission.action,
            is_system_permission=False,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(duplicate_resource_action)

        try:
            db.commit()
        except IntegrityError:
            duplicate_resource_action_rejected = True
            db.rollback()

        if not duplicate_resource_action_rejected:
            errors.append(
                "Duplicate Platform permission resource/action was accepted."
            )

        duplicate_mapping_rejected = False

        duplicate_mapping = PlatformRolePermission(
            organization_id=primary.id,
            platform_role_id=primary_role.id,
            platform_permission_id=permission.id,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(duplicate_mapping)

        try:
            db.commit()
        except IntegrityError:
            duplicate_mapping_rejected = True
            db.rollback()

        if not duplicate_mapping_rejected:
            errors.append(
                "Duplicate role-permission mapping was accepted."
            )

        duplicate_assignment_rejected = False

        duplicate_assignment = PlatformRoleAssignment(
            organization_id=primary.id,
            platform_user_id=primary_user.id,
            platform_role_id=primary_role.id,
            assigned_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(duplicate_assignment)

        try:
            db.commit()
        except IntegrityError:
            duplicate_assignment_rejected = True
            db.rollback()

        if not duplicate_assignment_rejected:
            errors.append(
                "Duplicate user-role assignment was accepted."
            )

        missing_role_fk_rejected = False

        missing_role_assignment = PlatformRoleAssignment(
            organization_id=primary.id,
            platform_user_id=primary_user.id,
            platform_role_id=str(uuid.uuid4()),
            assigned_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(missing_role_assignment)

        try:
            db.commit()
        except IntegrityError:
            missing_role_fk_rejected = True
            db.rollback()

        if not missing_role_fk_rejected:
            errors.append(
                "Assignment referencing an unknown Platform Role was accepted."
            )

        missing_permission_fk_rejected = False

        missing_permission_mapping = PlatformRolePermission(
            organization_id=primary.id,
            platform_role_id=primary_role.id,
            platform_permission_id=str(uuid.uuid4()),
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(missing_permission_mapping)

        try:
            db.commit()
        except IntegrityError:
            missing_permission_fk_rejected = True
            db.rollback()

        if not missing_permission_fk_rejected:
            errors.append(
                "Mapping referencing an unknown permission was accepted."
            )

        # Individual foreign keys confirm that every referenced row exists.
        # They do not prove that the Organization column matches the
        # Organization owned by the referenced Platform User or Platform Role.
        cross_organization_assignment = PlatformRoleAssignment(
            organization_id=primary.id,
            platform_user_id=secondary_user.id,
            platform_role_id=primary_role.id,
            assigned_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(cross_organization_assignment)

        cross_organization_assignment_stored = False

        try:
            db.commit()
            db.refresh(cross_organization_assignment)
            cross_organization_assignment_stored = True
        except IntegrityError:
            db.rollback()

        if not cross_organization_assignment_stored:
            errors.append(
                "Expected individual-FK tenant-boundary test could not run."
            )

        secondary_permission = PlatformPermission(
            permission_key=f"platform-users.manage.{suffix}",
            name="Manage Platform Users",
            description=(
                "Manage Platform User records in the "
                "Administration Workspace."
            ),
            resource="platform-users",
            action=f"manage-{suffix}",
            is_system_permission=True,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(secondary_permission)
        db.commit()
        db.refresh(secondary_permission)

        # Use a different permission so the role-permission uniqueness
        # constraint does not mask the Organization-boundary test.
        cross_organization_mapping = PlatformRolePermission(
            organization_id=secondary.id,
            platform_role_id=primary_role.id,
            platform_permission_id=secondary_permission.id,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(cross_organization_mapping)

        cross_organization_mapping_stored = False

        try:
            db.commit()
            db.refresh(cross_organization_mapping)
            cross_organization_mapping_stored = True
        except IntegrityError:
            db.rollback()

        if not cross_organization_mapping_stored:
            errors.append(
                "Expected role-mapping tenant-boundary test could not run."
            )

        legitimate_assignment_count = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == primary.id,
                PlatformRoleAssignment.platform_user_id
                == primary_user.id,
                PlatformRoleAssignment.platform_role_id
                == primary_role.id,
            )
            .count()
        )

        legitimate_mapping_count = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == primary.id,
                PlatformRolePermission.platform_role_id
                == primary_role.id,
                PlatformRolePermission.platform_permission_id
                == permission.id,
            )
            .count()
        )

        if legitimate_assignment_count != 1:
            errors.append(
                "Legitimate assignment count is incorrect."
            )

        if legitimate_mapping_count != 1:
            errors.append(
                "Legitimate mapping count is incorrect."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Primary Organization ID: {primary.id}")
        print(f"Secondary Organization ID: {secondary.id}")
        print(f"Platform Permission ID: {permission.id}")
        print(f"Primary Platform Role ID: {primary_role.id}")
        print(f"Platform Role Mapping ID: {mapping.id}")
        print(f"Platform Role Assignment ID: {assignment.id}")
        print(
            "Role Organization binding persisted: "
            f"{primary_role.organization_id == primary.id}"
        )
        print(
            "Permission vocabulary global: "
            f"{not hasattr(permission, 'organization_id')}"
        )
        print(
            "Role-permission mapping persisted: "
            f"{persisted_mapping is not None}"
        )
        print(
            "User-role assignment persisted: "
            f"{persisted_assignment is not None}"
        )
        print(
            "Duplicate Organization role key rejected: "
            f"{duplicate_role_rejected}"
        )
        print(
            "Duplicate permission key rejected: "
            f"{duplicate_permission_key_rejected}"
        )
        print(
            "Duplicate resource/action rejected: "
            f"{duplicate_resource_action_rejected}"
        )
        print(
            "Duplicate role-permission mapping rejected: "
            f"{duplicate_mapping_rejected}"
        )
        print(
            "Duplicate user-role assignment rejected: "
            f"{duplicate_assignment_rejected}"
        )
        print(
            "Unknown role foreign key rejected: "
            f"{missing_role_fk_rejected}"
        )
        print(
            "Unknown permission foreign key rejected: "
            f"{missing_permission_fk_rejected}"
        )
        print(
            "Cross-Organization assignment blocked by "
            "individual foreign keys: "
            f"{not cross_organization_assignment_stored}"
        )
        print(
            "Cross-Organization mapping blocked by "
            "individual foreign keys: "
            f"{not cross_organization_mapping_stored}"
        )
        print(
            "Service-layer tenant validation required: True"
        )
        print("Default roles seeded: False")
        print("Default permissions seeded: False")

        print()
        print("Validation: PASSED")
        print(
            "Platform authorization persistence enforces entity existence "
            "and uniqueness while explicitly preserving the requirement "
            "that future services validate cross-record Organization "
            "consistency before creating mappings or assignments."
        )

        return 0

    finally:
        db.rollback()

        if organization_ids:
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

            (
                db.query(PlatformUser)
                .filter(
                    PlatformUser.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(PlatformPermission)
                .filter(
                    PlatformPermission.permission_key.like(
                        f"%{suffix}%"
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
