import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)

from app.connectors.microsoft.EntraProvider import EntraProvider
from app.domain.principal_type import PrincipalType


SOURCE_SYSTEM = "Microsoft Entra ID"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def unique_source_identifiers(
    records: list[dict],
    label: str,
    errors: list[str],
) -> None:
    identifiers = [
        record.get("source_identifier")
        for record in records
    ]

    require(
        all(identifiers),
        f"{label} contains a missing source identifier.",
        errors,
    )

    present = [
        identifier
        for identifier in identifiers
        if identifier
    ]

    require(
        len(present) == len(set(present)),
        f"{label} contains duplicate source identifiers.",
        errors,
    )


def main() -> int:
    print("USOP RC-004 Live Microsoft Entra Collection Gate")
    print("------------------------------------------------")
    print("Persistence: disabled")
    print("Tenant-specific counts: prohibited")
    print()

    provider = EntraProvider()
    collected = provider.collect()

    identities = collected.get("identities", [])
    accounts = collected.get("accounts", [])
    groups = collected.get("groups", [])
    memberships = collected.get("memberships", [])
    roles = collected.get("roles", [])
    assignments = collected.get("role_assignments", [])

    print(f"Identities:       {len(identities)}")
    print(f"Accounts:         {len(accounts)}")
    print(f"Groups:           {len(groups)}")
    print(f"Memberships:      {len(memberships)}")
    print(f"Roles:            {len(roles)}")
    print(f"Role assignments: {len(assignments)}")
    print()

    errors: list[str] = []

    for label, records in (
        ("Identities", identities),
        ("Accounts", accounts),
        ("Groups", groups),
        ("Memberships", memberships),
        ("Roles", roles),
        ("Role assignments", assignments),
    ):
        require(
            isinstance(records, list),
            f"{label} collection is not a list.",
            errors,
        )

        unique_source_identifiers(
            records,
            label,
            errors,
        )

    identity_ids = {
        item.get("source_identifier")
        for item in identities
        if item.get("source_identifier")
    }

    account_ids = {
        item.get("source_identifier")
        for item in accounts
        if item.get("source_identifier")
    }

    group_ids = {
        item.get("source_identifier")
        for item in groups
        if item.get("source_identifier")
    }

    role_ids = {
        item.get("source_identifier")
        for item in roles
        if item.get("source_identifier")
    }

    for account in accounts:
        require(
            account.get("identity_source_identifier")
            in identity_ids,
            "Account does not resolve to a collected identity.",
            errors,
        )

        require(
            account.get("source_system") == SOURCE_SYSTEM,
            "Account has an unexpected source system.",
            errors,
        )

    for group in groups:
        require(
            group.get("source_system") == SOURCE_SYSTEM,
            "Group has an unexpected source system.",
            errors,
        )

    for membership in memberships:
        require(
            membership.get("subject_type")
            == PrincipalType.ACCOUNT.value,
            "Membership has an unexpected principal type.",
            errors,
        )

        require(
            membership.get("subject_source_identifier")
            in account_ids,
            "Membership does not resolve to a collected account.",
            errors,
        )

        require(
            membership.get("group_source_identifier")
            in group_ids,
            "Membership does not resolve to a collected group.",
            errors,
        )

        require(
            membership.get("membership_type") == "Direct",
            "Membership is not classified as Direct.",
            errors,
        )

        require(
            membership.get("status") == "Active",
            "Membership is not Active.",
            errors,
        )

    for role in roles:
        require(
            role.get("role_type") == "Directory",
            "Role does not use the Directory role type.",
            errors,
        )

        require(
            role.get("status") == "Active",
            "Role is not Active.",
            errors,
        )

    for assignment in assignments:
        require(
            assignment.get("subject_type")
            == PrincipalType.ACCOUNT.value,
            "Role assignment has an unexpected principal type.",
            errors,
        )

        require(
            assignment.get("subject_source_identifier")
            in account_ids,
            "Role assignment does not resolve to a collected account.",
            errors,
        )

        require(
            assignment.get("role_source_identifier")
            in role_ids,
            "Role assignment does not resolve to a collected role.",
            errors,
        )

        require(
            assignment.get("assignment_type") == "Direct",
            "Role assignment is not classified as Direct.",
            errors,
        )

        require(
            assignment.get("status") == "Active",
            "Role assignment is not Active.",
            errors,
        )

    if errors:
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print("Validation: PASSED")
    print(
        "Live Microsoft Entra collection satisfies the "
        "provider-neutral structural contract."
    )
    print()
    print(
        "No tenant-specific object counts or role names "
        "were assumed."
    )
    print(
        "No records were written to PostgreSQL."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())