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
from app.models.group import Group
from app.synchronization.sync_engine import (
    SynchronizationEngine,
)


SOURCE_SYSTEM = "Microsoft Entra ID"


def main() -> int:
    print("USOP Live Microsoft Entra Group Sync Test")
    print("-----------------------------------------")
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

        groups = (
            db.query(Group)
            .filter(
                Group.source_system
                == SOURCE_SYSTEM
            )
            .order_by(
                Group.name
            )
            .all()
        )

        print()
        print(
            "Microsoft Entra groups stored: "
            f"{len(groups)}"
        )
        print()

        validation_errors: list[str] = []
        source_identifiers: set[str] = set()

        for group in groups:
            print("-" * 60)
            print(f"Name: {group.name}")
            print(
                "Display name: "
                f"{group.display_name}"
            )
            print(
                "Group type: "
                f"{group.group_type}"
            )
            print(
                f"Status: {group.status}"
            )
            print(
                f"System: {group.system_name}"
            )
            print(
                "Description present: "
                f"{bool(group.description)}"
            )
            print(
                "Source identifier present: "
                f"{bool(group.source_identifier)}"
            )

            if not group.source_identifier:
                validation_errors.append(
                    f"Group '{group.name}' does not have "
                    "a source identifier."
                )
            elif (
                group.source_identifier
                in source_identifiers
            ):
                validation_errors.append(
                    f"Group '{group.name}' has a duplicate "
                    "source identifier."
                )
            else:
                source_identifiers.add(
                    group.source_identifier
                )

            if group.system_name != SOURCE_SYSTEM:
                validation_errors.append(
                    f"Group '{group.name}' has an unexpected "
                    "system name."
                )

            if group.group_type != "Security":
                validation_errors.append(
                    f"Group '{group.name}' was expected to "
                    "normalize as Security."
                )

            if group.status != "Active":
                validation_errors.append(
                    f"Group '{group.name}' was expected to "
                    "have Active status."
                )

        if len(groups) != 5:
            validation_errors.append(
                "Expected 5 live Microsoft Entra groups, "
                f"but found {len(groups)}."
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
            "Every live Microsoft Entra group was "
            "persisted with provider-neutral metadata."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
