import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)

from app.connectors.microsoft.EntraProvider import EntraProvider


def mask_username(value: str | None) -> str:
    """
    Mask account usernames before writing them to terminal output.
    """

    if not value:
        return "Unavailable"

    if "@" not in value:
        visible = value[:2]
        masked = "*" * max(len(value) - 2, 3)
        return f"{visible}{masked}"

    local_part, domain = value.split("@", 1)
    visible = local_part[:2]
    masked = "*" * max(len(local_part) - 2, 3)

    return f"{visible}{masked}@{domain}"


def validate_collection(
    collected: dict[str, Any],
) -> list[str]:
    """
    Validate the connector collection contract without persisting records.
    """

    errors: list[str] = []

    identities = collected.get("identities")
    accounts = collected.get("accounts")

    if not isinstance(identities, list):
        errors.append(
            "The identities collection is missing or is not a list."
        )
        identities = []

    if not isinstance(accounts, list):
        errors.append(
            "The accounts collection is missing or is not a list."
        )
        accounts = []

    identity_identifiers = {
        identity.get("source_identifier")
        for identity in identities
        if isinstance(identity, dict)
        and identity.get("source_identifier")
    }

    for index, account in enumerate(accounts, start=1):
        if not isinstance(account, dict):
            errors.append(
                f"Account record {index} is not an object."
            )
            continue

        required_fields = (
            "username",
            "account_type",
            "status",
            "system_name",
            "source_system",
            "source_identifier",
            "identity_source_system",
            "identity_source_identifier",
        )

        for field_name in required_fields:
            if not account.get(field_name):
                errors.append(
                    f"Account record {index} is missing "
                    f"'{field_name}'."
                )

        identity_source_identifier = account.get(
            "identity_source_identifier"
        )

        if (
            identity_source_identifier
            and identity_source_identifier
            not in identity_identifiers
        ):
            errors.append(
                f"Account record {index} does not correlate to a "
                "collected identity."
            )

    return errors


def main() -> int:
    print("USOP Live Microsoft Entra Account Collection Test")
    print("------------------------------------------------")
    print("Provider: microsoft-entra")
    print("Persistence: disabled")
    print()

    provider = EntraProvider()
    collected = provider.collect()

    identities = collected.get("identities", [])
    accounts = collected.get("accounts", [])

    print(f"Identities collected: {len(identities)}")
    print(f"Accounts collected: {len(accounts)}")
    print()

    validation_errors = validate_collection(collected)

    if validation_errors:
        print("Validation: FAILED")

        for error in validation_errors:
            print(f"- {error}")

        return 1

    print("Validation: PASSED")
    print(
        "Every collected account contains a provider-neutral "
        "identity correlation reference."
    )

    if len(accounts) != len(identities):
        print()
        print(
            "Notice: Identity and account counts differ. This can occur "
            "when a Graph user does not have a usable "
            "userPrincipalName."
        )

    print()
    print("Collected account samples:")

    for account in accounts[:10]:
        print("-" * 50)
        print(
            "Username: "
            f"{mask_username(account.get('username'))}"
        )
        print(
            "Display name present: "
            f"{bool(account.get('display_name'))}"
        )
        print(
            "Account type: "
            f"{account.get('account_type')}"
        )
        print(
            "Status: "
            f"{account.get('status')}"
        )
        print(
            "System: "
            f"{account.get('system_name')}"
        )
        print(
            "Source identifier present: "
            f"{bool(account.get('source_identifier'))}"
        )
        print(
            "Identity correlation present: "
            f"{bool(account.get('identity_source_identifier'))}"
        )

    print()
    print(
        "No records were normalized, reconciled, or written to "
        "PostgreSQL."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())