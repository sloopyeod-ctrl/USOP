import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import inspect


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


def main() -> int:
    print("USOP Generalized Membership Model Test")
    print("--------------------------------------")

    db = SessionLocal()

    try:
        table_inspector = inspect(
            db.get_bind()
        )

        columns = {
            column["name"]
            for column in table_inspector.get_columns(
                "memberships"
            )
        }

        expected_columns = {
            "subject_type",
            "subject_id",
            "group_id",
        }

        missing_columns = (
            expected_columns - columns
        )

        if missing_columns:
            print("Validation: FAILED")
            print(
                "Missing canonical membership columns: "
                f"{sorted(missing_columns)}"
            )
            return 1

        if "account_id" in columns:
            print("Validation: FAILED")
            print(
                "Legacy account_id remains in the "
                "memberships table."
            )
            return 1

        memberships = (
            db.query(Membership)
            .order_by(Membership.id)
            .all()
        )

        print(
            f"Membership records: {len(memberships)}"
        )

        validation_errors: list[str] = []

        for membership in memberships:
            print("-" * 60)
            print(f"ID: {membership.id}")
            print(
                "Subject type: "
                f"{membership.subject_type}"
            )
            print(
                "Subject ID present: "
                f"{bool(membership.subject_id)}"
            )
            print(
                "Group ID present: "
                f"{bool(membership.group_id)}"
            )
            print(
                "Source: "
                f"{membership.source_system}"
            )

            if (
                membership.subject_type
                != PrincipalType.ACCOUNT.value
            ):
                validation_errors.append(
                    "Existing membership was not migrated "
                    "as an Account principal."
                )

            account = (
                db.query(Account)
                .filter(
                    Account.id
                    == membership.subject_id
                )
                .first()
            )

            if account is None:
                validation_errors.append(
                    "Migrated membership subject does not "
                    "resolve to an account."
                )

            group = (
                db.query(Group)
                .filter(
                    Group.id
                    == membership.group_id
                )
                .first()
            )

            if group is None:
                validation_errors.append(
                    "Migrated membership target does not "
                    "resolve to a group."
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
            "Memberships now use canonical subject "
            "references and existing data was preserved."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())