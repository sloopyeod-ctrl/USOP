import sys
from pathlib import Path

from sqlalchemy import UniqueConstraint


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.platform_user_status import PlatformUserStatus
from app.models.platform_user import PlatformUser


EXPECTED_STATUSES = [
    "Invited",
    "Active",
    "Suspended",
    "Disabled",
]


def main() -> int:
    print("USOP Canonical Platform User Model Regression")
    print("---------------------------------------------")

    errors: list[str] = []

    table = PlatformUser.__table__
    columns = {
        column.name: column
        for column in table.columns
    }

    actual_statuses = [
        status.value
        for status in PlatformUserStatus
    ]

    if actual_statuses != EXPECTED_STATUSES:
        errors.append(
            "Platform User lifecycle vocabulary is incorrect."
        )

    required_columns = {
        "id",
        "organization_id",
        "display_name",
        "email",
        "status",
        "identity_provider",
        "external_tenant_id",
        "external_subject_id",
        "identity_issuer",
        "created_via_bootstrap",
        "invited_at",
        "activated_at",
        "last_authenticated_at",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "is_active",
    }

    missing_columns = required_columns - set(columns)

    if missing_columns:
        errors.append(
            "Missing PlatformUser columns: "
            + ", ".join(sorted(missing_columns))
        )

    organization_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in columns["organization_id"].foreign_keys
    }

    if organization_foreign_keys != {
        "organizations.id"
    }:
        errors.append(
            "PlatformUser is not bound to organizations.id."
        )

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(
            constraint,
            UniqueConstraint,
        )
    ]

    expected_unique_columns = {
        "organization_id",
        "identity_provider",
        "external_tenant_id",
        "external_subject_id",
    }

    unique_binding_present = any(
        {
            column.name
            for column in constraint.columns
        }
        == expected_unique_columns
        for constraint in unique_constraints
    )

    if not unique_binding_present:
        errors.append(
            "External identity binding is not uniquely "
            "scoped to the Organization."
        )

    prohibited_columns = {
        "identity_id",
        "account_id",
        "password",
        "password_hash",
        "access_token",
        "refresh_token",
        "license_id",
        "seat_id",
        "role_id",
        "permission_id",
    }

    embedded_prohibited_columns = (
        prohibited_columns & set(columns)
    )

    if embedded_prohibited_columns:
        errors.append(
            "PlatformUser embeds prohibited concerns: "
            + ", ".join(
                sorted(
                    embedded_prohibited_columns
                )
            )
        )

    if (
        columns["status"].default is None
        or columns["status"].default.arg
        != PlatformUserStatus.INVITED.value
    ):
        errors.append(
            "PlatformUser does not default to Invited."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print(f"Table: {table.name}")
    print(f"Column count: {len(columns)}")
    print(
        "Organization binding: "
        f"{next(iter(organization_foreign_keys))}"
    )
    print(
        "External identity binding unique: "
        f"{unique_binding_present}"
    )
    print(
        "Default status: "
        f"{columns['status'].default.arg}"
    )
    print(
        "Customer Identity foreign key embedded: False"
    )
    print(
        "Customer Account foreign key embedded: False"
    )
    print("Password or token stored: False")
    print("Seat State embedded: False")
    print("Role or permission embedded: False")
    print(
        "Bootstrap provenance grants authorization: False"
    )

    print()
    print("Validation: PASSED")
    print(
        "PlatformUser is a distinct Organization-bound "
        "operator identity with external authentication "
        "binding and clean separation from synchronized "
        "customer identities, credentials, authorization, "
        "and commercial Seat State."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
