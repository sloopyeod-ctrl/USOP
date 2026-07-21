import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import inspect, text


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)


from app.database.session import SessionLocal
from app.models.audit_event import AuditEvent
from app.models.knowledge_asset import KnowledgeAsset
from app.models.organization import Organization


PROFILE_KNOWLEDGE_ASSET_COMMITTED_CREATION = (
    "knowledge-asset-committed-creation"
)

PROFILE_ORGANIZATION_NAME_PREFIXES = {
    PROFILE_KNOWLEDGE_ASSET_COMMITTED_CREATION: (
        "Knowledge Asset Committed Creation "
    ),
}

SUPPORTED_ORGANIZATION_TABLES = {
    PROFILE_KNOWLEDGE_ASSET_COMMITTED_CREATION: {
        "knowledge_assets",
    },
}

PROTECTED_ORGANIZATION_NAMES = {
    "USOP Development",
}

PROTECTED_ORGANIZATION_SLUGS = {
    "usop-development",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or remove allowlisted USOP engineering "
            "verification data."
        )
    )

    parser.add_argument(
        "--profile",
        choices=sorted(
            PROFILE_ORGANIZATION_NAME_PREFIXES
        ),
        default=(
            PROFILE_KNOWLEDGE_ASSET_COMMITTED_CREATION
        ),
        help=(
            "Allowlisted verification-data profile to inspect "
            "or clean."
        ),
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Perform cleanup. Without this option, the utility "
            "runs in dry-run mode."
        ),
    )

    return parser.parse_args()


def organization_owned_counts(
    db,
    *,
    organization_id: str,
) -> dict[str, int]:
    inspector = inspect(db.bind)
    counts: dict[str, int] = {}

    for table_name in inspector.get_table_names():
        columns = {
            column["name"]
            for column in inspector.get_columns(table_name)
        }

        if "organization_id" not in columns:
            continue

        quoted_table = inspector.dialect.identifier_preparer.quote(
            table_name
        )

        count = db.execute(
            text(
                f"SELECT COUNT(*) FROM {quoted_table} "
                "WHERE organization_id = :organization_id"
            ),
            {
                "organization_id": organization_id,
            },
        ).scalar_one()

        if count:
            counts[table_name] = int(count)

    return counts


def matching_audit_events(
    db,
    *,
    organization_id: str,
    knowledge_asset_ids: set[str],
) -> list[AuditEvent]:
    events = db.query(AuditEvent).all()
    matches: list[AuditEvent] = []

    for event in events:
        metadata = event.metadata_json

        metadata_organization_id = (
            metadata.get("organization_id")
            if isinstance(metadata, dict)
            else None
        )

        references_asset = (
            event.entity_type == "KnowledgeAsset"
            and event.entity_id in knowledge_asset_ids
        )

        references_organization = (
            metadata_organization_id == organization_id
        )

        if references_asset or references_organization:
            matches.append(event)

    return matches


def require_safe_organization(
    organization: Organization,
    *,
    required_name_prefix: str,
) -> None:
    if organization.name in PROTECTED_ORGANIZATION_NAMES:
        raise RuntimeError(
            "Cleanup refused to target a protected Organization."
        )

    if organization.slug in PROTECTED_ORGANIZATION_SLUGS:
        raise RuntimeError(
            "Cleanup refused to target a protected Organization."
        )

    if not organization.name.startswith(
        required_name_prefix
    ):
        raise RuntimeError(
            "Cleanup refused because the Organization name "
            "does not match the selected verification profile."
        )


def main() -> int:
    args = parse_args()

    required_name_prefix = (
        PROFILE_ORGANIZATION_NAME_PREFIXES[
            args.profile
        ]
    )

    supported_tables = (
        SUPPORTED_ORGANIZATION_TABLES[
            args.profile
        ]
    )

    db = SessionLocal()

    try:
        organizations = (
            db.query(Organization)
            .filter(
                Organization.name.startswith(
                    required_name_prefix
                )
            )
            .order_by(
                Organization.created_at.asc(),
                Organization.id.asc(),
            )
            .all()
        )

        mode = "EXECUTE" if args.execute else "DRY RUN"

        print(
            "USOP Engineering Verification Data Cleanup"
        )
        print(
            "------------------------------------------"
        )
        print(f"Mode: {mode}")
        print(f"Profile: {args.profile}")
        print(
            "Organization prefix: "
            f"{required_name_prefix}"
        )
        print(
            "Matching Organizations: "
            f"{len(organizations)}"
        )
        print()

        if not organizations:
            print("No matching verification data was found.")
            return 0

        cleanup_plan = []

        for organization in organizations:
            require_safe_organization(
                organization,
                required_name_prefix=required_name_prefix,
            )

            owned_counts = organization_owned_counts(
                db,
                organization_id=organization.id,
            )

            unsupported_tables = (
                set(owned_counts) - supported_tables
            )

            if unsupported_tables:
                raise RuntimeError(
                    "Cleanup refused because Organization "
                    f"{organization.id} owns records in unsupported "
                    "tables: "
                    + ", ".join(
                        sorted(unsupported_tables)
                    )
                )

            knowledge_assets = (
                db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.organization_id
                    == organization.id
                )
                .order_by(
                    KnowledgeAsset.created_at.asc(),
                    KnowledgeAsset.id.asc(),
                )
                .all()
            )

            knowledge_asset_ids = {
                asset.id
                for asset in knowledge_assets
            }

            audit_events = matching_audit_events(
                db,
                organization_id=organization.id,
                knowledge_asset_ids=knowledge_asset_ids,
            )

            cleanup_plan.append(
                (
                    organization,
                    knowledge_assets,
                    audit_events,
                    owned_counts,
                )
            )

            print(
                f"Organization: {organization.id}"
            )
            print(f"  Name: {organization.name}")
            print(f"  Slug: {organization.slug}")
            print(
                "  KnowledgeAssets: "
                f"{len(knowledge_assets)}"
            )
            print(
                "  Related AuditEvents: "
                f"{len(audit_events)}"
            )

            if owned_counts:
                print("  Organization-owned rows:")

                for table_name, count in sorted(
                    owned_counts.items()
                ):
                    print(
                        f"    {table_name}: {count}"
                    )

            print()

        if not args.execute:
            print(
                "Dry run complete. No records were changed."
            )
            print(
                "Run again with --execute to perform this "
                "allowlisted cleanup."
            )
            return 0

        deleted_audits = 0
        deleted_assets = 0
        deleted_organizations = 0

        for (
            organization,
            knowledge_assets,
            audit_events,
            _,
        ) in cleanup_plan:
            for audit_event in audit_events:
                db.delete(audit_event)
                deleted_audits += 1

            for knowledge_asset in knowledge_assets:
                db.delete(knowledge_asset)
                deleted_assets += 1

            db.flush()

            db.delete(organization)
            deleted_organizations += 1

        db.commit()

        remaining = (
            db.query(Organization)
            .filter(
                Organization.name.startswith(
                    required_name_prefix
                )
            )
            .count()
        )

        if remaining:
            raise RuntimeError(
                "Cleanup verification failed because matching "
                "Organizations remain."
            )

        protected_organization = (
            db.query(Organization)
            .filter(
                Organization.slug
                == "usop-development"
            )
            .one_or_none()
        )

        if protected_organization is None:
            raise RuntimeError(
                "Cleanup verification failed because the "
                "protected USOP Development Organization "
                "could not be found."
            )

        print("Cleanup: PASSED")
        print(
            f"Deleted AuditEvents: {deleted_audits}"
        )
        print(
            f"Deleted KnowledgeAssets: {deleted_assets}"
        )
        print(
            "Deleted Organizations: "
            f"{deleted_organizations}"
        )
        print(
            "Protected Organization preserved: "
            f"{protected_organization.name}"
        )

        return 0

    except Exception as error:
        db.rollback()
        print(f"Cleanup: FAILED")
        print(str(error))
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
