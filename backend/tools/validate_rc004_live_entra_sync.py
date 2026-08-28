import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)

from app.database.session import SessionLocal
from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.synchronization.sync_engine import SynchronizationEngine


ORGANIZATION_ID = os.environ.get("RC004_ORGANIZATION_ID")

if not ORGANIZATION_ID:
    raise SystemExit("RC004_ORGANIZATION_ID is required.")


def count(db, model) -> int:
    return db.scalar(
        select(func.count()).select_from(model)
    )


def snapshot(db) -> dict[str, int]:
    return {
        "identities": count(db, Identity),
        "accounts": count(db, Account),
        "groups": count(db, Group),
        "memberships": count(db, Membership),
        "roles": count(db, Role),
        "role_assignments": count(db, RoleAssignment),
    }


def duplicate_source_count(db, model) -> int:
    source_system = model.source_system
    source_identifier = model.source_identifier

    rows = db.execute(
        select(
            source_system,
            source_identifier,
            func.count().label("count"),
        )
        .where(source_identifier.is_not(None))
        .group_by(
            source_system,
            source_identifier,
        )
        .having(func.count() > 1)
    ).all()

    return len(rows)


def run_sync(label: str) -> dict:
    db = SessionLocal()

    try:
        engine = SynchronizationEngine(
            db=db,
            organization_id=ORGANIZATION_ID,
        )

        result = engine.run("microsoft-entra")

        print(f"\n=== {label} ===")
        print(f"status={result['status']}")
        print(f"errors={result['errors']}")
        print(f"created={result['created']}")
        print(f"updated={result['updated']}")
        print(f"metadata={result['metadata']}")

        if result["status"] != "success":
            raise RuntimeError(
                f"{label} synchronization did not succeed."
            )

        if result["errors"]:
            raise RuntimeError(
                f"{label} returned synchronization errors."
            )

        current = snapshot(db)

        print("canonical_counts=", current)

        return current

    finally:
        db.close()


def main() -> int:
    first = run_sync("FIRST LIVE ENTRA SYNC")
    second = run_sync("SECOND LIVE ENTRA SYNC")

    print("\n=== IDEMPOTENCY ===")
    print("first=", first)
    print("second=", second)

    if first != second:
        raise RuntimeError(
            "Canonical counts changed on identical second sync."
        )

    db = SessionLocal()

    try:
        models = (
            ("identities", Identity),
            ("accounts", Account),
            ("groups", Group),
            ("memberships", Membership),
            ("roles", Role),
            ("role_assignments", RoleAssignment),
        )

        duplicate_failures = []

        for label, model in models:
            duplicates = duplicate_source_count(
                db,
                model,
            )

            print(
                f"{label}_duplicate_source_identifiers="
                f"{duplicates}"
            )

            if duplicates:
                duplicate_failures.append(label)

        if duplicate_failures:
            raise RuntimeError(
                "Duplicate provider identities detected: "
                + ", ".join(duplicate_failures)
            )

    finally:
        db.close()

    print()
    print("Validation: PASSED")
    print(
        "Live Entra synchronization remained stable "
        "across two consecutive reconciliation passes."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())