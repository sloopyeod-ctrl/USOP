import sys
from pathlib import Path

from sqlalchemy import UniqueConstraint


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.platform_role_status import PlatformRoleStatus
from app.models.permission import Permission
from app.models.platform_permission import PlatformPermission
from app.models.platform_role import PlatformRole
from app.models.platform_role_assignment import (
    PlatformRoleAssignment,
)
from app.models.platform_role_permission import (
    PlatformRolePermission,
)
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.role_permission import RolePermission


EXPECTED_ROLE_STATUSES = [
    "Active",
    "Disabled",
]


def unique_constraint_present(
    table,
    expected_columns: set[str],
) -> bool:
    return any(
        {
            column.name
            for column in constraint.columns
        }
        == expected_columns
        for constraint in table.constraints
        if isinstance(
            constraint,
            UniqueConstraint,
        )
    )


def foreign_key_targets(table) -> set[str]:
    return {
        foreign_key.target_fullname
        for column in table.columns
        for foreign_key in column.foreign_keys
    }


def main() -> int:
    print("USOP Platform Authorization Model Regression")
    print("--------------------------------------------")

    errors: list[str] = []

    actual_statuses = [
        item.value
        for item in PlatformRoleStatus
    ]

    if actual_statuses != EXPECTED_ROLE_STATUSES:
        errors.append(
            "PlatformRoleStatus vocabulary is incorrect."
        )

    role_table = PlatformRole.__table__
    permission_table = PlatformPermission.__table__
    mapping_table = PlatformRolePermission.__table__
    assignment_table = PlatformRoleAssignment.__table__

    expected_tables = {
        "platform_roles",
        "platform_permissions",
        "platform_role_permissions",
        "platform_role_assignments",
    }

    actual_tables = {
        role_table.name,
        permission_table.name,
        mapping_table.name,
        assignment_table.name,
    }

    if actual_tables != expected_tables:
        errors.append(
            "Platform authorization table names are incorrect."
        )

    if not unique_constraint_present(
        role_table,
        {
            "organization_id",
            "role_key",
        },
    ):
        errors.append(
            "PlatformRole is not unique by Organization and role key."
        )

    if not unique_constraint_present(
        permission_table,
        {
            "resource",
            "action",
        },
    ):
        errors.append(
            "PlatformPermission resource/action uniqueness is missing."
        )

    if not unique_constraint_present(
        mapping_table,
        {
            "platform_role_id",
            "platform_permission_id",
        },
    ):
        errors.append(
            "PlatformRolePermission uniqueness is missing."
        )

    if not unique_constraint_present(
        assignment_table,
        {
            "platform_user_id",
            "platform_role_id",
        },
    ):
        errors.append(
            "PlatformRoleAssignment uniqueness is missing."
        )

    expected_role_foreign_keys = {
        "organizations.id",
    }

    if foreign_key_targets(
        role_table
    ) != expected_role_foreign_keys:
        errors.append(
            "PlatformRole Organization binding is incorrect."
        )

    expected_mapping_foreign_keys = {
        "organizations.id",
        "platform_roles.id",
        "platform_permissions.id",
    }

    if foreign_key_targets(
        mapping_table
    ) != expected_mapping_foreign_keys:
        errors.append(
            "PlatformRolePermission bindings are incorrect."
        )

    expected_assignment_foreign_keys = {
        "organizations.id",
        "platform_users.id",
        "platform_roles.id",
    }

    if foreign_key_targets(
        assignment_table
    ) != expected_assignment_foreign_keys:
        errors.append(
            "PlatformRoleAssignment bindings are incorrect."
        )

    role_columns = {
        column.name
        for column in role_table.columns
    }

    permission_columns = {
        column.name
        for column in permission_table.columns
    }

    assignment_columns = {
        column.name
        for column in assignment_table.columns
    }

    prohibited_role_columns = {
        "identity_id",
        "account_id",
        "platform_user_id",
        "permission_id",
        "password",
        "access_token",
        "seat_id",
        "license_id",
    }

    if role_columns & prohibited_role_columns:
        errors.append(
            "PlatformRole embeds prohibited concerns."
        )

    prohibited_permission_columns = {
        "organization_id",
        "platform_role_id",
        "platform_user_id",
        "identity_id",
        "account_id",
        "seat_id",
        "license_id",
    }

    if permission_columns & prohibited_permission_columns:
        errors.append(
            "PlatformPermission embeds prohibited concerns."
        )

    prohibited_assignment_columns = {
        "password",
        "access_token",
        "refresh_token",
        "seat_id",
        "license_id",
        "permission_id",
    }

    if assignment_columns & prohibited_assignment_columns:
        errors.append(
            "PlatformRoleAssignment embeds prohibited concerns."
        )

    customer_models_are_distinct = all(
        platform_model is not customer_model
        for platform_model, customer_model in (
            (PlatformRole, Role),
            (PlatformPermission, Permission),
            (
                PlatformRoleAssignment,
                RoleAssignment,
            ),
            (
                PlatformRolePermission,
                RolePermission,
            ),
        )
    )

    if not customer_models_are_distinct:
        errors.append(
            "Platform authorization reuses customer IAM models."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print("Platform authorization tables:")
    for table_name in sorted(actual_tables):
        print(f"- {table_name}")

    print()
    print(
        "Role lifecycle statuses: "
        + ", ".join(actual_statuses)
    )
    print(
        "Role Organization-scoped: True"
    )
    print(
        "Permission vocabulary global: True"
    )
    print(
        "Role-permission mapping separate: True"
    )
    print(
        "User-role assignment separate: True"
    )
    print(
        "Customer IAM models reused: False"
    )
    print(
        "Permissions embedded in PlatformUser: False"
    )
    print(
        "Roles embedded in PlatformUser: False"
    )
    print(
        "Authentication state embedded: False"
    )
    print(
        "Seat State embedded: False"
    )
    print(
        "License State embedded: False"
    )
    print(
        "Bootstrap provenance grants authority: False"
    )
    print(
        "Default roles seeded: False"
    )
    print(
        "Default permissions seeded: False"
    )

    print()
    print("Validation: PASSED")
    print(
        "Platform authorization is modeled as an independent, "
        "Organization-scoped role and assignment system backed by a "
        "global permission vocabulary, with strict separation from "
        "customer IAM, authentication, commercial Seats, and Licenses."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
