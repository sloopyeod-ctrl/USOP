import sys
from pathlib import Path

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

from app.database.session import SessionLocal
from app.domain.principal_type import PrincipalType
from app.models.account import Account
from app.models.group import Group
from app.models.membership import Membership
from app.synchronization.sync_engine import (
    SynchronizationEngine,
)


SOURCE_SYSTEM = "Microsoft Entra ID"
EXPECTED_MEMBERSHIPS = 9


def mask_username(
    value: str | None,
) -> str:
    if not value:
        return "Unavailable"

    if "@" not in value:
        return f"{value[:2]}***"

    local_part, domain = value.split(
        "@",
        1,
    )

    return f"{local_part[:2]}***@{domain}"


def main() -> int:
    print("USOP Live Microsoft Entra Membership Sync Test")
    print("----------------------------------------------")
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
        print(
            f"Created: {result['created']}"
        )
        print(
            f"Updated: {result['updated']}"
        )
        print(
            "Duration: "
            f"{result['duration_seconds']} seconds"
        )

        if result["errors"]:
            print(
                f"Errors: {result['errors']}"
            )
            return 1

        memberships = (
            db.query(Membership)
            .filter(
                Membership.source_system
                == SOURCE_SYSTEM
            )
            .order_by(
                Membership.source_identifier
            )
            .all()
        )

        accounts = (
            db.query(Account)
            .filter(
                Account.source_system
                == SOURCE_SYSTEM
            )
            .all()
        )

        groups = (
            db.query(Group)
            .filter(
                Group.source_system
                == SOURCE_SYSTEM
            )
            .all()
        )

        accounts_by_id = {
            account.id: account
            for account in accounts
        }

        groups_by_id = {
            group.id: group
            for group in groups
        }

        print()
        print(
            "Microsoft Entra memberships stored: "
            f"{len(memberships)}"
        )

        validation_errors: list[str] = []
        source_identifiers: set[str] = set()

        for membership in memberships:
            account = accounts_by_id.get(
                membership.subject_id
            )
            group = groups_by_id.get(
                membership.group_id
            )

            print("-" * 60)
            print(
                "Subject type: "
                f"{membership.subject_type}"
            )
            print(
                "Account resolved: "
                f"{account is not None}"
            )
            print(
                "Group resolved: "
                f"{group is not None}"
            )
            print(
                "Membership type: "
                f"{membership.membership_type}"
            )
            print(
                f"Status: {membership.status}"
            )
            print(
                "Source identifier present: "
                f"{bool(membership.source_identifier)}"
            )

            if account:
                print(
                    "Account: "
                    f"{mask_username(account.username)}"
                )

            if group:
                print(
                    f"Group: {group.name}"
                )

            if (
                membership.subject_type
                != PrincipalType.ACCOUNT.value
            ):
                validation_errors.append(
                    "A live membership has an unexpected "
                    "principal type."
                )

            if account is None:
                validation_errors.append(
                    "A live membership does not resolve to "
                    "a live Microsoft Entra account."
                )

            if group is None:
                validation_errors.append(
                    "A live membership does not resolve to "
                    "a live Microsoft Entra group."
                )

            if not membership.source_identifier:
                validation_errors.append(
                    "A live membership does not contain a "
                    "source identifier."
                )
            elif (
                membership.source_identifier
                in source_identifiers
            ):
                validation_errors.append(
                    "Duplicate live membership source "
                    "identifier detected."
                )
            else:
                source_identifiers.add(
                    membership.source_identifier
                )

            if membership.membership_type != "Direct":
                validation_errors.append(
                    "A live membership was expected to be "
                    "a Direct relationship."
                )

            if membership.status != "Active":
                validation_errors.append(
                    "A live membership was expected to have "
                    "Active status."
                )

        if len(memberships) != EXPECTED_MEMBERSHIPS:
            validation_errors.append(
                f"Expected {EXPECTED_MEMBERSHIPS} live "
                "memberships, but found "
                f"{len(memberships)}."
            )

        if validation_errors:
            print()
            print("Validation: FAILED")

            for error in validation_errors:
                print(f"- {error}")

            return 1

        print()
        print("Validation: PASSED")
        print(
            "Every live Microsoft Entra membership was "
            "resolved and persisted as a canonical "
            "principal-to-group relationship."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())