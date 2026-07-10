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

from app.database.session import SessionLocal
from app.models.account import Account
from app.models.identity import Identity
from app.synchronization.sync_engine import (
    SynchronizationEngine,
)


SOURCE_SYSTEM = "Microsoft Entra ID"


def mask_identifier(
    value: str | None,
) -> str:
    if not value:
        return "Unavailable"

    if "@" not in value:
        visible = value[:2]
        masked = "*" * max(
            len(value) - 2,
            3,
        )
        return f"{visible}{masked}"

    local_part, domain = value.split(
        "@",
        1,
    )
    visible = local_part[:2]
    masked = "*" * max(
        len(local_part) - 2,
        3,
    )

    return f"{visible}{masked}@{domain}"


def main() -> int:
    print("USOP Live Identity and Account Sync Test")
    print("----------------------------------------")
    print("Provider: microsoft-entra")

    db = SessionLocal()

    try:
        engine = SynchronizationEngine(db)
        result = engine.run(
            "microsoft-entra"
        )

        print()
        print(f"Status: {result['status']}")
        print(
            f"Collected: {result['collected']}"
        )
        print(
            f"Normalized: {result['normalized']}"
        )
        print(f"Created: {result['created']}")
        print(f"Updated: {result['updated']}")
        print(
            "Duration: "
            f"{result['duration_seconds']} seconds"
        )

        if result["errors"]:
            print(
                f"Errors: {result['errors']}"
            )
            return 1

        identities = (
            db.query(Identity)
            .filter(
                Identity.source_system
                == SOURCE_SYSTEM
            )
            .order_by(
                Identity.display_name
            )
            .all()
        )

        accounts = (
            db.query(Account)
            .filter(
                Account.source_system
                == SOURCE_SYSTEM
            )
            .order_by(
                Account.username
            )
            .all()
        )

        print()
        print(
            "Microsoft Entra identities stored: "
            f"{len(identities)}"
        )
        print(
            "Microsoft Entra accounts stored: "
            f"{len(accounts)}"
        )

        identity_by_id = {
            identity.id: identity
            for identity in identities
        }

        validation_errors: list[str] = []

        for account in accounts:
            identity = identity_by_id.get(
                account.identity_id
            )

            if identity is None:
                validation_errors.append(
                    "A live account is not linked to a "
                    "live Microsoft Entra identity."
                )
                continue

            if (
                account.source_identifier
                != identity.source_identifier
            ):
                validation_errors.append(
                    "A live account source identifier "
                    "does not match its linked identity."
                )

        print()
        print("Stored account links:")

        for account in accounts:
            identity = identity_by_id.get(
                account.identity_id
            )

            print("-" * 50)
            print(
                "Username: "
                f"{mask_identifier(account.username)}"
            )
            print(
                "Account status: "
                f"{account.status}"
            )
            print(
                "Account type: "
                f"{account.account_type}"
            )
            print(
                "Identity linked: "
                f"{identity is not None}"
            )
            print(
                "Source identifiers match: "
                f"{bool(identity) and account.source_identifier == identity.source_identifier}"
            )

            if identity:
                print(
                    "Identity: "
                    f"{identity.display_name}"
                )

        if validation_errors:
            print()
            print("Validation: FAILED")

            for error in validation_errors:
                print(f"- {error}")

            return 1

        if len(accounts) != len(identities):
            print()
            print(
                "Validation: FAILED"
            )
            print(
                "- The number of live accounts does "
                "not match the number of live identities."
            )
            return 1

        print()
        print("Validation: PASSED")
        print(
            "Every live Microsoft Entra account is "
            "linked to its corresponding identity."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())