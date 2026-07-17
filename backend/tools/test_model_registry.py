import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path("backend").resolve()
sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

import app.models
from app.database.base import Base


def main():
    required_tables = {
        "access_reviews",
        "accounts",
        "audit_events",
        "governance_policies",
        "groups",
        "identities",
        "identity_attributes",
        "memberships",
        "organizations",
        "licenses",
        "platform_users",
    "permissions",
        "review_campaigns",
        "role_assignments",
        "role_permissions",
        "roles",
    }

    registered_tables = set(
        Base.metadata.tables.keys()
    )

    missing_tables = (
        required_tables - registered_tables
    )

    print("USOP SQLAlchemy Model Registry Test")
    print("-----------------------------------")

    for table_name in sorted(
        registered_tables
    ):
        print(f"- {table_name}")

    print()

    if missing_tables:
        print("Validation: FAILED")
        print("Missing tables:")

        for table_name in sorted(
            missing_tables
        ):
            print(f"- {table_name}")

        raise SystemExit(1)

    access_review_table = (
        Base.metadata.tables["access_reviews"]
    )

    campaign_foreign_keys = [
        str(foreign_key.target_fullname)
        for foreign_key
        in access_review_table.foreign_keys
        if foreign_key.parent.name
        == "campaign_id"
    ]

    if (
        "review_campaigns.id"
        not in campaign_foreign_keys
    ):
        print("Validation: FAILED")
        print(
            "Access review campaign foreign key "
            "was not resolved."
        )
        raise SystemExit(1)

    print("Validation: PASSED")
    print(
        "All mapped tables and foreign-key "
        "dependencies are registered."
    )


if __name__ == "__main__":
    main()
