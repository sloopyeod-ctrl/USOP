import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)

from app.connectors.microsoft.EntraProvider import (
    EntraProvider,
)
from app.domain.principal_type import PrincipalType


EXPECTED_ROLES = 7
EXPECTED_ASSIGNMENTS = 7
EXPECTED_PRINCIPALS = 3
EXPECTED_ROLE_NAMES = {
    "Attribute Provisioning Reader",
    "Billing Administrator",
    "Compliance Administrator",
    "Directory Readers",
    "Global Administrator",
    "Security Operator",
    "User Administrator",
}


def validate_collection(
    collected: dict[str, Any],
) -> list[str]:
    """
    Validate assigned role and role-assignment collection without persistence.
    """

    errors: list[str] = []

    roles = collected.get("roles")
    assignments = collected.get(
        "role_assignments"
    )
    accounts = collected.get("accounts")

    if not isinstance(roles, list):
        return [
            "The roles collection is missing or is not a list."
        ]

    if not isinstance(assignments, list):
        return [
            "The role assignments collection is missing or "
            "is not a list."
        ]

    if not isinstance(accounts, list):
        errors.append(
            "The accounts collection is missing or is not a list."
        )
        accounts = []

    role_source_identifiers = {
        role.get("source_identifier")
        for role in roles
        if isinstance(role, dict)
        and role.get("source_identifier")
    }

    account_source_identifiers = {
        account.get("source_identifier")
        for account in accounts
        if isinstance(account, dict)
        and account.get("source_identifier")
    }

    role_names = {
        role.get("name")
        for role in roles
        if isinstance(role, dict)
        and role.get("name")
    }

    role_relationship_identifiers: set[str] = set()
    referenced_principals: set[str] = set()

    required_role_fields = (
        "name",
        "display_name",
        "role_type",
        "status",
        "system_name",
        "source_system",
        "source_identifier",
    )

    for index, role in enumerate(
        roles,
        start=1,
    ):
        if not isinstance(role, dict):
            errors.append(
                f"Role record {index} is not an object."
            )
            continue

        for field_name in required_role_fields:
            if not role.get(field_name):
                errors.append(
                    f"Role record {index} is missing "
                    f"'{field_name}'."
                )

        if role.get("role_type") != "Directory":
            errors.append(
                f"Role record {index} was expected to use "
                "the Directory role type."
            )

        if role.get("status") != "Active":
            errors.append(
                f"Role record {index} was expected to have "
                "Active status."
            )

    required_assignment_fields = (
        "subject_type",
        "subject_source_system",
        "subject_source_identifier",
        "role_source_system",
        "role_source_identifier",
        "assignment_type",
        "status",
        "directory_scope",
        "source_system",
        "source_identifier",
    )

    for index, assignment in enumerate(
        assignments,
        start=1,
    ):
        if not isinstance(assignment, dict):
            errors.append(
                f"Role assignment record {index} is not "
                "an object."
            )
            continue

        for field_name in required_assignment_fields:
            if not assignment.get(field_name):
                errors.append(
                    f"Role assignment record {index} is "
                    f"missing '{field_name}'."
                )

        subject_type = assignment.get(
            "subject_type"
        )
        subject_source_identifier = assignment.get(
            "subject_source_identifier"
        )
        role_source_identifier = assignment.get(
            "role_source_identifier"
        )
        relationship_identifier = assignment.get(
            "source_identifier"
        )

        if (
            subject_type
            != PrincipalType.ACCOUNT.value
        ):
            errors.append(
                f"Role assignment record {index} has an "
                "unexpected principal type."
            )

        if (
            subject_source_identifier
            not in account_source_identifiers
        ):
            errors.append(
                f"Role assignment record {index} references "
                "an account that was not collected."
            )

        if subject_source_identifier:
            referenced_principals.add(
                subject_source_identifier
            )

        if (
            role_source_identifier
            not in role_source_identifiers
        ):
            errors.append(
                f"Role assignment record {index} references "
                "a role that was not collected."
            )

        if assignment.get(
            "assignment_type"
        ) != "Direct":
            errors.append(
                f"Role assignment record {index} was "
                "expected to be Direct."
            )

        if assignment.get("status") != "Active":
            errors.append(
                f"Role assignment record {index} was "
                "expected to have Active status."
            )

        if assignment.get(
            "directory_scope"
        ) != "/":
            errors.append(
                f"Role assignment record {index} was "
                "expected to have tenant-wide scope."
            )

        if relationship_identifier:
            if (
                relationship_identifier
                in role_relationship_identifiers
            ):
                errors.append(
                    f"Role assignment record {index} has a "
                    "duplicate source identifier."
                )

            role_relationship_identifiers.add(
                relationship_identifier
            )

    if len(roles) != EXPECTED_ROLES:
        errors.append(
            f"Expected {EXPECTED_ROLES} assigned role "
            f"definitions, but collected {len(roles)}."
        )

    if len(assignments) != EXPECTED_ASSIGNMENTS:
        errors.append(
            f"Expected {EXPECTED_ASSIGNMENTS} active role "
            f"assignments, but collected {len(assignments)}."
        )

    if len(referenced_principals) != EXPECTED_PRINCIPALS:
        errors.append(
            f"Expected {EXPECTED_PRINCIPALS} distinct "
            "assigned principals, but collected "
            f"{len(referenced_principals)}."
        )

    if role_names != EXPECTED_ROLE_NAMES:
        errors.append(
            "The collected role names do not match the "
            "currently assigned tenant role set."
        )

    return errors


def main() -> int:
    print(
        "USOP Live Microsoft Entra Assigned Role "
        "Collection Test"
    )
    print(
        "------------------------------------------------"
    )
    print("Provider: microsoft-entra")
    print("Persistence: disabled")
    print()

    provider = EntraProvider()
    collected = provider.collect()

    identities = collected.get(
        "identities",
        [],
    )
    accounts = collected.get(
        "accounts",
        [],
    )
    groups = collected.get(
        "groups",
        [],
    )
    memberships = collected.get(
        "memberships",
        [],
    )
    roles = collected.get(
        "roles",
        [],
    )
    assignments = collected.get(
        "role_assignments",
        [],
    )

    print(
        f"Identities collected: {len(identities)}"
    )
    print(
        f"Accounts collected: {len(accounts)}"
    )
    print(
        f"Groups collected: {len(groups)}"
    )
    print(
        f"Memberships collected: {len(memberships)}"
    )
    print(
        f"Assigned roles collected: {len(roles)}"
    )
    print(
        "Active role assignments collected: "
        f"{len(assignments)}"
    )
    print()

    validation_errors = validate_collection(
        collected
    )

    if validation_errors:
        print("Validation: FAILED")

        for error in validation_errors:
            print(f"- {error}")

        return 1

    print("Validation: PASSED")
    print(
        "Only role definitions referenced by active "
        "assignments were collected."
    )
    print()

    print("Assigned role definitions:")

    for role in sorted(
        roles,
        key=lambda item: item["name"],
    ):
        print("-" * 60)
        print(f"Role: {role.get('name')}")
        print(
            "Description present: "
            f"{bool(role.get('description'))}"
        )
        print(
            "Source identifier present: "
            f"{bool(role.get('source_identifier'))}"
        )

    print()
    print("Active role assignments:")

    for assignment in assignments:
        print("-" * 60)
        print(
            "Subject type: "
            f"{assignment.get('subject_type')}"
        )
        print(
            "Subject source identifier present: "
            f"{bool(assignment.get('subject_source_identifier'))}"
        )
        print(
            "Role source identifier present: "
            f"{bool(assignment.get('role_source_identifier'))}"
        )
        print(
            "Assignment type: "
            f"{assignment.get('assignment_type')}"
        )
        print(
            "Directory scope: "
            f"{assignment.get('directory_scope')}"
        )
        print(
            "Source identifier present: "
            f"{bool(assignment.get('source_identifier'))}"
        )

    print()
    print(
        "No role or role-assignment records were "
        "normalized, reconciled, or written to PostgreSQL."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())