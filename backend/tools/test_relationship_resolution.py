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
from app.models.account import Account
from app.models.group import Group
from app.models.role import Role
from app.reconciliation.reconciliation_engine import (
    ReconciliationEngine,
)


SOURCE_SYSTEM = "Microsoft Entra ID"


def main() -> int:
    print("USOP Canonical Relationship Resolution Test")
    print("-------------------------------------------")

    db = SessionLocal()

    try:
        engine = ReconciliationEngine(db)

        account = (
            db.query(Account)
            .filter(
                Account.source_system == SOURCE_SYSTEM,
                Account.source_identifier.is_not(None),
                Account.is_active.is_(True),
            )
            .first()
        )

        group = (
            db.query(Group)
            .filter(
                Group.source_system == SOURCE_SYSTEM,
                Group.source_identifier.is_not(None),
                Group.is_active.is_(True),
            )
            .first()
        )

        role = (
            db.query(Role)
            .filter(
                Role.source_system == SOURCE_SYSTEM,
                Role.source_identifier.is_not(None),
                Role.is_active.is_(True),
            )
            .first()
        )

        missing = []

        if account is None:
            missing.append("live Microsoft Entra account")

        if group is None:
            missing.append("live Microsoft Entra group")

        if role is None:
            missing.append("live Microsoft Entra role")

        if missing:
            print("Validation: FAILED")
            print(
                "Missing required canonical records: "
                + ", ".join(missing)
            )
            return 1

        resolved_account = engine._resolve_account_reference(
            source_system=account.source_system,
            source_identifier=account.source_identifier,
        )

        resolved_group = engine._resolve_group_reference(
            source_system=group.source_system,
            source_identifier=group.source_identifier,
        )

        resolved_role = engine._resolve_role_reference(
            source_system=role.source_system,
            source_identifier=role.source_identifier,
        )

        errors = []

        if resolved_account is None:
            errors.append(
                "The account provider reference did not resolve."
            )
        elif resolved_account.id != account.id:
            errors.append(
                "The account provider reference resolved incorrectly."
            )

        if resolved_group is None:
            errors.append(
                "The group provider reference did not resolve."
            )
        elif resolved_group.id != group.id:
            errors.append(
                "The group provider reference resolved incorrectly."
            )

        if resolved_role is None:
            errors.append(
                "The role provider reference did not resolve."
            )
        elif resolved_role.id != role.id:
            errors.append(
                "The role provider reference resolved incorrectly."
            )

        if engine._resolve_account_reference(None, None) is not None:
            errors.append(
                "An empty account provider reference unexpectedly resolved."
            )

        if engine._resolve_group_reference(None, None) is not None:
            errors.append(
                "An empty group provider reference unexpectedly resolved."
            )

        if engine._resolve_role_reference(None, None) is not None:
            errors.append(
                "An empty role provider reference unexpectedly resolved."
            )

        if errors:
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print("Account reference resolved: True")
        print("Group reference resolved: True")
        print("Role reference resolved: True")
        print()
        print("Validation: PASSED")
        print(
            "Canonical provider references now use shared "
            "relationship-resolution helpers."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())