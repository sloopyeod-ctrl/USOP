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


def validate_collection(
    collected: dict[str, Any],
) -> list[str]:
    """
    Validate the connector group collection contract without persistence.
    """

    errors: list[str] = []

    groups = collected.get("groups")

    if not isinstance(groups, list):
        return [
            "The groups collection is missing or is not a list."
        ]

    source_identifiers: set[str] = set()

    for index, group in enumerate(
        groups,
        start=1,
    ):
        if not isinstance(group, dict):
            errors.append(
                f"Group record {index} is not an object."
            )
            continue

        required_fields = (
            "name",
            "display_name",
            "group_type",
            "status",
            "system_name",
            "source_system",
            "source_identifier",
        )

        for field_name in required_fields:
            if not group.get(field_name):
                errors.append(
                    f"Group record {index} is missing "
                    f"'{field_name}'."
                )

        source_identifier = group.get(
            "source_identifier"
        )

        if source_identifier:
            if source_identifier in source_identifiers:
                errors.append(
                    f"Group record {index} contains a "
                    "duplicate source identifier."
                )

            source_identifiers.add(
                source_identifier
            )

    return errors


def main() -> int:
    print(
        "USOP Live Microsoft Entra Group Collection Test"
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

    print(
        f"Identities collected: {len(identities)}"
    )
    print(
        f"Accounts collected: {len(accounts)}"
    )
    print(
        f"Groups collected: {len(groups)}"
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
        "Every collected group contains a stable "
        "provider source identifier."
    )
    print()

    print("Collected groups:")

    for group in groups:
        print("-" * 60)
        print(
            f"Name: {group.get('name')}"
        )
        print(
            "Display name present: "
            f"{bool(group.get('display_name'))}"
        )
        print(
            f"Group type: {group.get('group_type')}"
        )
        print(
            f"Status: {group.get('status')}"
        )
        print(
            f"System: {group.get('system_name')}"
        )
        print(
            "Description present: "
            f"{bool(group.get('description'))}"
        )
        print(
            "Source identifier present: "
            f"{bool(group.get('source_identifier'))}"
        )

    print()
    print(
        "No group records were normalized, reconciled, "
        "or written to PostgreSQL."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
