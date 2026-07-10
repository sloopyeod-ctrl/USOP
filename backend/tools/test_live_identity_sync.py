import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(dotenv_path=ENV_FILE, override=False)

from app.database.session import SessionLocal
from app.models.identity import Identity
from app.synchronization.sync_engine import SynchronizationEngine


def mask_email(value: str | None) -> str:
    if not value or "@" not in value:
        return "Unavailable"

    local_part, domain = value.split("@", 1)
    visible = local_part[:2]
    masked = "*" * max(len(local_part) - 2, 3)

    return f"{visible}{masked}@{domain}"


def main() -> int:
    print("USOP Live Identity Synchronization Test")
    print("---------------------------------------")
    print("Provider: microsoft-entra")

    db = SessionLocal()

    try:
        engine = SynchronizationEngine(db)
        result = engine.run("microsoft-entra")

        print()
        print(f"Status: {result['status']}")
        print(f"Collected: {result['collected']}")
        print(f"Normalized: {result['normalized']}")
        print(f"Created: {result['created']}")
        print(f"Updated: {result['updated']}")
        print(f"Duration: {result['duration_seconds']} seconds")

        if result["errors"]:
            print(f"Errors: {result['errors']}")
            return 1

        identities = (
            db.query(Identity)
            .filter(
                Identity.source_system == "Microsoft Entra ID"
            )
            .order_by(Identity.display_name)
            .all()
        )

        print()
        print(
            "Microsoft Entra identities stored: "
            f"{len(identities)}"
        )

        for identity in identities:
            print("-" * 40)
            print(f"Name: {identity.display_name}")
            print(f"Email: {mask_email(identity.primary_email)}")
            print(f"Status: {identity.status}")
            print(f"Source: {identity.source_system}")
            print(
                "Source identifier present: "
                f"{bool(identity.source_identifier)}"
            )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
