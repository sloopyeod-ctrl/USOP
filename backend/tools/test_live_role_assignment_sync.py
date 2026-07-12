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
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.synchronization.sync_engine import (
    SynchronizationEngine,
)


SOURCE_SYSTEM = "Microsoft Entra ID"
EXPECTED_ASSIGNMENTS = 7
EXPECTED_PRINCIPALS = 3


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
    print(
        "USOP Live Microsoft Entra Role Assignment "
        "Sync Test"
    )
    print(
        "----------------------------------------------"
    )
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

        assignments = (
            db.query(RoleAssignment)
            .filter(
                RoleAssignment.source_system
                == SOURCE_SYSTEM
            )
            .order_by(
                RoleAssignment.source_identifier
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

        roles = (
            db.query(Role)
            .filter(
                Role.source_system
                == SOURCE_SYSTEM
            )
            .all()
        )

        accounts_by_id = {
            account.id: account
            for account in accounts
        }

        roles_by_id = {
            role.id: role
            for role in roles
        }

        print()
        print(
            "Microsoft Entra role assignments stored: "
            f"{len(assignments)}"
        )

        validation_errors: list[str] = []
        source_identifiers: set[str] = set()
        principal_ids: set[str] = set()

        for assignment in assignments:
            account = accounts_by_id.get(
                assignment.subject_id
            )
            role = roles_by_id.get(
                assignment.role_id
            )

            print("-" * 60)
            print(
                "Subject type: "
                f"{assignment.subject_type}"
            )
            print(
                "Account resolved: "
                f"{account is not None}"
            )
            print(
                "Role resolved: "
                f"{role is not None}"
            )
            print(
                "Assignment type: "
                f"{assignment.assignment_type}"
            )
            print(
                f"Status: {assignment.status}"
            )
            print(
                "Directory scope: "
                f"{assignment.directory_scope}"
            )
            print(
                "Application scope: "
                f"{assignment.application_scope}"
            )
            print(
                "Source identifier present: "
                f"{bool(assignment.source_identifier)}"
            )

            if account:
                print(
                    "Account: "
                    f"{mask_username(account.username)}"
                )
                principal_ids.add(
                    account.id
                )

            if role:
                print(
                    f"Role: {role.name}"
                )

            if (
                assignment.subject_type
                != PrincipalType.ACCOUNT.value
            ):
                validation_errors.append(
                    "A live role assignment has an "
                    "unexpected principal type."
                )

            if account is None:
                validation_errors.append(
                    "A live role assignment does not resolve "
                    "to a live Microsoft Entra account."
                )

            if role is None:
                validation_errors.append(
                    "A live role assignment does not resolve "
                    "to a live Microsoft Entra role."
                )

            if assignment.assignment_type != "Direct":
                validation_errors.append(
                    "A live role assignment was expected to "
                    "be Direct."
                )

            if assignment.status != "Active":
                validation_errors.append(
                    "A live role assignment was expected to "
                    "have Active status."
                )

            if assignment.directory_scope != "/":
                validation_errors.append(
                    "A live role assignment was expected to "
                    "have tenant-wide directory scope."
                )

            if assignment.application_scope is not None:
                validation_errors.append(
                    "A live role assignment unexpectedly has "
                    "an application scope."
                )

            if not assignment.source_identifier:
                validation_errors.append(
                    "A live role assignment does not contain "
                    "a source identifier."
                )
            elif (
                assignment.source_identifier
                in source_identifiers
            ):
                validation_errors.append(
                    "Duplicate live role-assignment source "
                    "identifier detected."
                )
            else:
                source_identifiers.add(
                    assignment.source_identifier
                )

        if len(assignments) != EXPECTED_ASSIGNMENTS:
            validation_errors.append(
                f"Expected {EXPECTED_ASSIGNMENTS} live role "
                "assignments, but found "
                f"{len(assignments)}."
            )

        if len(principal_ids) != EXPECTED_PRINCIPALS:
            validation_errors.append(
                f"Expected {EXPECTED_PRINCIPALS} distinct "
                "assigned principals, but found "
                f"{len(principal_ids)}."
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
            "Every active Microsoft Entra role assignment "
            "was resolved and persisted as a scoped "
            "canonical principal-to-role relationship."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())