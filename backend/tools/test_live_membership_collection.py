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

from app.domain.principal_type import PrincipalType
from app.connectors.microsoft.EntraProvider import (
    EntraProvider,
)


def validate_collection(
    collected: dict[str, Any],
) -> list[str]:
    """
    Validate live membership collection without persistence.
    """

    errors: list[str] = []

    memberships = collected.get("memberships")
    groups = collected.get("groups")
    accounts = collected.get("accounts")

    if not isinstance(memberships, list):
        return [
            "The memberships collection is missing or is not a list."
        ]

    if not isinstance(groups, list):
        errors.append(
            "The groups collection is missing or is not a list."
        )
        groups = []

    if not isinstance(accounts, list):
        errors.append(
            "The accounts collection is missing or is not a list."
        )
        accounts = []

    group_source_identifiers = {
        group.get("source_identifier")
        for group in groups
        if isinstance(group, dict)
        and group.get("source_identifier")
    }

    account_source_identifiers = {
        account.get("source_identifier")
        for account in accounts
        if isinstance(account, dict)
        and account.get("source_identifier")
    }

    membership_source_identifiers: set[str] = set()

    valid_principal_types = {
        principal_type.value
        for principal_type in PrincipalType
    }

    required_fields = (
        "subject_type",
        "subject_source_system",
        "subject_source_identifier",
        "group_source_system",
        "group_source_identifier",
        "membership_type",
        "status",
        "source_system",
        "source_identifier",
    )

    for index, membership in enumerate(
        memberships,
        start=1,
    ):
        if not isinstance(membership, dict):
            errors.append(
                f"Membership record {index} is not an object."
            )
            continue

        for field_name in required_fields:
            if not membership.get(field_name):
                errors.append(
                    f"Membership record {index} is missing "
                    f"'{field_name}'."
                )

        subject_type = membership.get(
            "subject_type"
        )
        subject_source_identifier = membership.get(
            "subject_source_identifier"
        )
        group_source_identifier = membership.get(
            "group_source_identifier"
        )
        source_identifier = membership.get(
            "source_identifier"
        )

        if (
            subject_type
            and subject_type not in valid_principal_types
        ):
            errors.append(
                f"Membership record {index} has an invalid "
                "canonical principal type."
            )

        if (
            subject_type
            == PrincipalType.ACCOUNT.value
            and subject_source_identifier
            not in account_source_identifiers
        ):
            errors.append(
                f"Membership record {index} references an "
                "account that was not collected."
            )

        if (
            group_source_identifier
            not in group_source_identifiers
        ):
            errors.append(
                f"Membership record {index} references a "
                "group that was not collected."
            )

        if source_identifier:
            if (
                source_identifier
                in membership_source_identifiers
            ):
                errors.append(
                    f"Membership record {index} has a "
                    "duplicate source identifier."
                )

            membership_source_identifiers.add(
                source_identifier
            )

    return errors


def main() -> int:
    print(
        "USOP Live Microsoft Entra Membership "
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
    print()

    validation_errors = validate_collection(
        collected
    )

    if len(memberships) != 9:
        validation_errors.append(
            "Expected 9 direct memberships in the current "
            f"test tenant, but collected {len(memberships)}."
        )

    if validation_errors:
        print("Validation: FAILED")

        for error in validation_errors:
            print(f"- {error}")

        return 1

    principal_type_counts: dict[str, int] = {}

    for membership in memberships:
        subject_type = membership[
            "subject_type"
        ]

        principal_type_counts[subject_type] = (
            principal_type_counts.get(
                subject_type,
                0,
            )
            + 1
        )

    print("Validation: PASSED")
    print(
        "Every collected membership contains canonical "
        "provider relationship references."
    )
    print()

    print("Principal type counts:")

    for principal_type in sorted(
        principal_type_counts
    ):
        print(
            f"- {principal_type}: "
            f"{principal_type_counts[principal_type]}"
        )

    print()
    print("Collected membership relationships:")

    for membership in memberships:
        print("-" * 60)
        print(
            "Subject type: "
            f"{membership.get('subject_type')}"
        )
        print(
            "Subject source identifier present: "
            f"{bool(membership.get('subject_source_identifier'))}"
        )
        print(
            "Group source identifier present: "
            f"{bool(membership.get('group_source_identifier'))}"
        )
        print(
            "Membership type: "
            f"{membership.get('membership_type')}"
        )
        print(
            f"Status: {membership.get('status')}"
        )
        print(
            "Relationship source identifier present: "
            f"{bool(membership.get('source_identifier'))}"
        )

    print()
    print(
        "No membership records were normalized, "
        "reconciled, or written to PostgreSQL."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
