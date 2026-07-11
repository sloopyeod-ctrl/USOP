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
from app.domain.role_type import RoleType
from app.models.role import Role
from app.synchronization.sync_engine import (
    SynchronizationEngine,
)


SOURCE_SYSTEM = "Microsoft Entra ID"
EXPECTED_ROLES = 7
EXPECTED_ROLE_NAMES = {
    "Attribute Provisioning Reader",
    "Billing Administrator",
    "Compliance Administrator",
    "Directory Readers",
    "Global Administrator",
    "Security Operator",
    "User Administrator",
}


def main() -> int:
    print(
        "USOP Live Microsoft Entra Assigned Role "
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

        roles = (
            db.query(Role)
            .filter(
                Role.source_system
                == SOURCE_SYSTEM
            )
            .order_by(
                Role.name
            )
            .all()
        )

        print()
        print(
            "Microsoft Entra assigned roles stored: "
            f"{len(roles)}"
        )

        validation_errors: list[str] = []
        source_identifiers: set[str] = set()

        role_names = {
            role.name
            for role in roles
        }

        for role in roles:
            print("-" * 60)
            print(f"Name: {role.name}")
            print(
                "Display name: "
                f"{role.display_name}"
            )
            print(
                "Role type: "
                f"{role.role_type}"
            )
            print(
                f"Status: {role.status}"
            )
            print(
                f"System: {role.system_name}"
            )
            print(
                "Description present: "
                f"{bool(role.description)}"
            )
            print(
                "Source identifier present: "
                f"{bool(role.source_identifier)}"
            )

            if role.role_type != RoleType.DIRECTORY.value:
                validation_errors.append(
                    f"Role '{role.name}' does not use the "
                    "Directory role type."
                )

            if role.status != "Active":
                validation_errors.append(
                    f"Role '{role.name}' does not have "
                    "Active status."
                )

            if role.system_name != SOURCE_SYSTEM:
                validation_errors.append(
                    f"Role '{role.name}' has an unexpected "
                    "system name."
                )

            if not role.description:
                validation_errors.append(
                    f"Role '{role.name}' does not contain "
                    "its provider description."
                )

            if not role.source_identifier:
                validation_errors.append(
                    f"Role '{role.name}' does not contain "
                    "a source identifier."
                )
            elif role.source_identifier in source_identifiers:
                validation_errors.append(
                    f"Role '{role.name}' has a duplicate "
                    "source identifier."
                )
            else:
                source_identifiers.add(
                    role.source_identifier
                )

        if len(roles) != EXPECTED_ROLES:
            validation_errors.append(
                f"Expected {EXPECTED_ROLES} assigned "
                "Microsoft Entra roles, but found "
                f"{len(roles)}."
            )

        if role_names != EXPECTED_ROLE_NAMES:
            validation_errors.append(
                "Stored role names do not match the "
                "assignment-driven tenant role set."
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
            "Only Microsoft Entra role definitions "
            "referenced by active assignments were "
            "normalized and persisted."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())