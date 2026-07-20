import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)


from app.database.session import SessionLocal
from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.models.knowledge_asset import KnowledgeAsset
from app.models.organization import Organization
from app.repositories.knowledge_asset_repository import (
    KnowledgeAssetRepository,
)


ACTOR = "USOP Knowledge Asset Repository Regression"


def build_knowledge_asset(
    *,
    organization_id: str,
    title: str,
    version: int,
    category: KnowledgeCategory,
    status: KnowledgeAssetStatus,
    is_active: bool = True,
) -> KnowledgeAsset:
    return KnowledgeAsset(
        organization_id=organization_id,
        title=title,
        summary=f"Summary for {title} version {version}.",
        guidance=f"Guidance for {title} version {version}.",
        category=category.value,
        status=status.value,
        version=version,
        source_system="USOPRegression",
        source_identifier=(
            f"{title.lower().replace(' ', '-')}-v{version}"
        ),
        confidence_score=100,
        created_by=ACTOR,
        updated_by=ACTOR,
        is_active=is_active,
    )


def main() -> int:
    print("USOP Knowledge Asset Repository Regression")
    print("------------------------------------------")

    db = SessionLocal()
    repository = KnowledgeAssetRepository(db)

    suffix = uuid.uuid4().hex

    primary_organization_id: str | None = None
    secondary_organization_id: str | None = None

    errors: list[str] = []

    try:
        primary_organization = Organization(
            name="Knowledge Asset Repository Primary",
            slug=f"knowledge-asset-primary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_organization = Organization(
            name="Knowledge Asset Repository Secondary",
            slug=f"knowledge-asset-secondary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(primary_organization)
        db.add(secondary_organization)
        db.flush()
        db.refresh(primary_organization)
        db.refresh(secondary_organization)

        primary_organization_id = primary_organization.id
        secondary_organization_id = secondary_organization.id

        naming_v1 = repository.create(
            build_knowledge_asset(
                organization_id=primary_organization.id,
                title="Snowflake Naming Convention",
                version=1,
                category=KnowledgeCategory.IDENTITY_RESOLUTION,
                status=KnowledgeAssetStatus.DEPRECATED,
            )
        )

        naming_v2 = repository.create(
            build_knowledge_asset(
                organization_id=primary_organization.id,
                title="Snowflake Naming Convention",
                version=2,
                category=KnowledgeCategory.IDENTITY_RESOLUTION,
                status=KnowledgeAssetStatus.ACTIVE,
            )
        )

        inactive_asset = repository.create(
            build_knowledge_asset(
                organization_id=primary_organization.id,
                title="Legacy Authentication Procedure",
                version=1,
                category=KnowledgeCategory.AUTHENTICATION,
                status=KnowledgeAssetStatus.RETIRED,
                is_active=False,
            )
        )

        secondary_asset = repository.create(
            build_knowledge_asset(
                organization_id=secondary_organization.id,
                title="Snowflake Naming Convention",
                version=7,
                category=KnowledgeCategory.IDENTITY_RESOLUTION,
                status=KnowledgeAssetStatus.ACTIVE,
            )
        )

        by_id = repository.get_by_id(
            organization_id=primary_organization.id,
            knowledge_asset_id=naming_v2.id,
        )

        if by_id is None:
            errors.append(
                "Organization-scoped lookup by ID returned no record."
            )
        elif by_id.id != naming_v2.id:
            errors.append(
                "Organization-scoped lookup by ID returned the wrong record."
            )

        cross_organization_lookup = repository.get_by_id(
            organization_id=secondary_organization.id,
            knowledge_asset_id=naming_v2.id,
        )

        if cross_organization_lookup is not None:
            errors.append(
                "Lookup by ID crossed the Organization boundary."
            )

        latest_version = repository.get_latest_version(
            organization_id=primary_organization.id,
            title="Snowflake Naming Convention",
        )

        if latest_version is None:
            errors.append(
                "Latest-version lookup returned no record."
            )
        elif latest_version.id != naming_v2.id:
            errors.append(
                "Latest-version lookup did not return the "
                "highest primary-Organization version."
            )

        latest_version_wrong_organization = (
            repository.get_latest_version(
                organization_id=secondary_organization.id,
                title="Snowflake Naming Convention",
            )
        )

        if latest_version_wrong_organization is None:
            errors.append(
                "Secondary Organization latest-version lookup "
                "returned no record."
            )
        elif (
            latest_version_wrong_organization.id
            != secondary_asset.id
        ):
            errors.append(
                "Latest-version lookup crossed the Organization boundary."
            )

        missing_latest_version = repository.get_latest_version(
            organization_id=primary_organization.id,
            title="Unknown Knowledge Asset",
        )

        if missing_latest_version is not None:
            errors.append(
                "Latest-version lookup returned a record for an "
                "unknown title."
            )

        organization_assets = repository.list_for_organization(
            primary_organization.id
        )

        organization_asset_ids = [
            asset.id
            for asset in organization_assets
        ]

        expected_organization_asset_ids = [
            inactive_asset.id,
            naming_v2.id,
            naming_v1.id,
        ]

        if (
            organization_asset_ids
            != expected_organization_asset_ids
        ):
            errors.append(
                "Organization listing was not deterministic by "
                "title ascending and version descending."
            )

        active_assets = repository.list_active(
            primary_organization.id
        )

        active_asset_ids = [
            asset.id
            for asset in active_assets
        ]

        expected_active_asset_ids = [
            naming_v2.id,
            naming_v1.id,
        ]

        if active_asset_ids != expected_active_asset_ids:
            errors.append(
                "Active listing included inactive records or used "
                "incorrect ordering."
            )

        identity_resolution_assets = (
            repository.list_by_category(
                organization_id=primary_organization.id,
                category=(
                    KnowledgeCategory.IDENTITY_RESOLUTION.value
                ),
            )
        )

        identity_resolution_ids = [
            asset.id
            for asset in identity_resolution_assets
        ]

        expected_identity_resolution_ids = [
            naming_v2.id,
            naming_v1.id,
        ]

        if (
            identity_resolution_ids
            != expected_identity_resolution_ids
        ):
            errors.append(
                "Category listing was not correctly Organization-scoped "
                "and version ordered."
            )

        secondary_assets = repository.list_for_organization(
            secondary_organization.id
        )

        if [
            asset.id
            for asset in secondary_assets
        ] != [secondary_asset.id]:
            errors.append(
                "Secondary Organization listing returned incorrect records."
            )

        prohibited_methods = {
            "list_all",
            "delete",
            "update",
            "approve",
            "activate",
            "retire",
            "calculate_version",
            "assign_owner",
            "link_decision",
            "authorize",
            "commit",
            "rollback",
        }

        exposed_prohibited_methods = sorted(
            method_name
            for method_name in prohibited_methods
            if hasattr(
                repository,
                method_name,
            )
        )

        if exposed_prohibited_methods:
            errors.append(
                "KnowledgeAssetRepository exposes prohibited methods: "
                + ", ".join(exposed_prohibited_methods)
            )

        db.rollback()

        persisted_primary_organization = (
            db.query(Organization)
            .filter(
                Organization.id
                == primary_organization.id,
            )
            .one_or_none()
        )

        persisted_secondary_organization = (
            db.query(Organization)
            .filter(
                Organization.id
                == secondary_organization.id,
            )
            .one_or_none()
        )

        persisted_asset_count = (
            db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.id.in_(
                    [
                        naming_v1.id,
                        naming_v2.id,
                        inactive_asset.id,
                        secondary_asset.id,
                    ]
                )
            )
            .count()
        )

        if persisted_primary_organization is not None:
            errors.append(
                "Repository unexpectedly committed the primary Organization."
            )

        if persisted_secondary_organization is not None:
            errors.append(
                "Repository unexpectedly committed the secondary Organization."
            )

        if persisted_asset_count != 0:
            errors.append(
                "Repository unexpectedly committed KnowledgeAsset records."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Knowledge Assets created: "
            f"{len(organization_assets) + len(secondary_assets)}"
        )
        print(f"Lookup by ID: {by_id is not None}")
        print(
            "Organization boundary preserved: "
            f"{cross_organization_lookup is None}"
        )
        print(
            "Latest primary version selected: "
            f"{latest_version.id == naming_v2.id}"
        )
        print(
            "Latest-version Organization isolation: "
            f"{latest_version_wrong_organization.id == secondary_asset.id}"
        )
        print(
            "Unknown title returns no latest version: "
            f"{missing_latest_version is None}"
        )
        print(
            "Organization listing deterministic: "
            f"{organization_asset_ids == expected_organization_asset_ids}"
        )
        print(
            "Active listing correct: "
            f"{active_asset_ids == expected_active_asset_ids}"
        )
        print(
            "Category listing correct: "
            f"{identity_resolution_ids == expected_identity_resolution_ids}"
        )
        print(
            "Secondary Organization isolated: "
            f"{len(secondary_assets) == 1}"
        )
        print(
            "Prohibited repository methods exposed: "
            f"{bool(exposed_prohibited_methods)}"
        )
        print(
            "Repository committed transaction: "
            f"{persisted_asset_count != 0}"
        )

        print()
        print("Validation: PASSED")
        print(
            "KnowledgeAssetRepository provides deterministic, "
            "Organization-scoped persistence, retrieval, and latest-version "
            "selection while preserving service-layer transaction ownership "
            "and separation from lifecycle rules, version allocation, "
            "authorization, workflow, and relationship management."
        )

        return 0

    finally:
        db.rollback()

        organization_ids = [
            organization_id
            for organization_id in (
                primary_organization_id,
                secondary_organization_id,
            )
            if organization_id is not None
        ]

        if organization_ids:
            (
                db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(Organization)
                .filter(
                    Organization.id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
