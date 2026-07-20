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
from app.services.knowledge_asset_service import (
    KnowledgeAssetDuplicateVersionError,
    KnowledgeAssetOrganizationNotFoundError,
    KnowledgeAssetService,
    KnowledgeAssetServiceError,
    KnowledgeAssetValidationError,
)


ACTOR = "USOP Knowledge Asset Service Regression"


def build_knowledge_asset(
    *,
    organization_id: str,
    title: str,
    version: int,
) -> KnowledgeAsset:
    return KnowledgeAsset(
        organization_id=organization_id,
        title=title,
        summary=f"Summary for {title}.",
        guidance=f"Guidance for {title}.",
        category=(
            KnowledgeCategory.IDENTITY_RESOLUTION.value
        ),
        status=KnowledgeAssetStatus.DRAFT.value,
        version=version,
        source_system="USOPRegression",
        source_identifier=(
            f"{title.lower().replace(' ', '-')}-v{version}"
        ),
        confidence_score=100,
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def main() -> int:
    print("USOP Knowledge Asset Service Foundation Regression")
    print("--------------------------------------------------")

    db = SessionLocal()
    service = KnowledgeAssetService(db)

    suffix = uuid.uuid4().hex

    primary_organization_id: str | None = None
    secondary_organization_id: str | None = None

    errors: list[str] = []

    try:
        primary_organization = Organization(
            name="Knowledge Asset Service Primary",
            slug=f"knowledge-asset-service-primary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_organization = Organization(
            name="Knowledge Asset Service Secondary",
            slug=f"knowledge-asset-service-secondary-{suffix}",
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

        primary_asset_v1 = build_knowledge_asset(
            organization_id=primary_organization.id,
            title="Snowflake Naming Convention",
            version=1,
        )

        primary_asset_v2 = build_knowledge_asset(
            organization_id=primary_organization.id,
            title="Snowflake Naming Convention",
            version=2,
        )

        secondary_asset = build_knowledge_asset(
            organization_id=secondary_organization.id,
            title="Secondary Organization Guidance",
            version=1,
        )

        db.add(primary_asset_v1)
        db.add(primary_asset_v2)
        db.add(secondary_asset)
        db.flush()
        db.refresh(primary_asset_v1)
        db.refresh(primary_asset_v2)
        db.refresh(secondary_asset)

        primary_assets = service.list_for_organization(
            primary_organization.id
        )

        primary_asset_ids = [
            asset.id
            for asset in primary_assets
        ]

        expected_primary_asset_ids = [
            primary_asset_v2.id,
            primary_asset_v1.id,
        ]

        if primary_asset_ids != expected_primary_asset_ids:
            errors.append(
                "KnowledgeAssetService did not preserve deterministic "
                "Organization-scoped repository ordering."
            )

        by_id = service.get_by_id(
            organization_id=primary_organization.id,
            knowledge_asset_id=primary_asset_v2.id,
        )

        if by_id is None:
            errors.append(
                "KnowledgeAsset lookup by ID returned no record."
            )
        elif by_id.id != primary_asset_v2.id:
            errors.append(
                "KnowledgeAsset lookup by ID returned the wrong record."
            )

        cross_organization_lookup = service.get_by_id(
            organization_id=secondary_organization.id,
            knowledge_asset_id=primary_asset_v2.id,
        )

        if cross_organization_lookup is not None:
            errors.append(
                "KnowledgeAssetService disclosed a cross-Organization record."
            )

        missing_asset = service.get_by_id(
            organization_id=primary_organization.id,
            knowledge_asset_id=str(uuid.uuid4()),
        )

        if missing_asset is not None:
            errors.append(
                "Unknown KnowledgeAsset lookup did not return None."
            )

        unknown_organization_list_rejected = False

        try:
            service.list_for_organization(
                str(uuid.uuid4())
            )
        except KnowledgeAssetOrganizationNotFoundError:
            unknown_organization_list_rejected = True

        if not unknown_organization_list_rejected:
            errors.append(
                "Unknown Organization listing was not rejected."
            )

        unknown_organization_get_rejected = False

        try:
            service.get_by_id(
                organization_id=str(uuid.uuid4()),
                knowledge_asset_id=primary_asset_v1.id,
            )
        except KnowledgeAssetOrganizationNotFoundError:
            unknown_organization_get_rejected = True

        if not unknown_organization_get_rejected:
            errors.append(
                "Unknown Organization lookup was not rejected."
            )

        exception_hierarchy_valid = all(
            issubclass(
                exception_type,
                KnowledgeAssetServiceError,
            )
            for exception_type in (
                KnowledgeAssetOrganizationNotFoundError,
                KnowledgeAssetValidationError,
                KnowledgeAssetDuplicateVersionError,
            )
        )

        if not exception_hierarchy_valid:
            errors.append(
                "KnowledgeAsset service exception hierarchy is invalid."
            )

        prohibited_methods = {
            "create",
            "create_version",
            "allocate_version",
            "approve",
            "activate",
            "deprecate",
            "retire",
            "delete",
            "authorize",
            "commit",
            "rollback",
        }

        exposed_prohibited_methods = sorted(
            method_name
            for method_name in prohibited_methods
            if hasattr(
                service,
                method_name,
            )
        )

        if exposed_prohibited_methods:
            errors.append(
                "Read-only KnowledgeAssetService exposes prohibited methods: "
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
                        primary_asset_v1.id,
                        primary_asset_v2.id,
                        secondary_asset.id,
                    ]
                )
            )
            .count()
        )

        if persisted_primary_organization is not None:
            errors.append(
                "Read-only service unexpectedly committed "
                "the primary Organization."
            )

        if persisted_secondary_organization is not None:
            errors.append(
                "Read-only service unexpectedly committed "
                "the secondary Organization."
            )

        if persisted_asset_count != 0:
            errors.append(
                "Read-only service unexpectedly committed "
                "KnowledgeAsset records."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Primary Knowledge Assets listed: "
            f"{len(primary_assets)}"
        )
        print(
            "Deterministic ordering preserved: "
            f"{primary_asset_ids == expected_primary_asset_ids}"
        )
        print(
            "Lookup by ID: "
            f"{by_id is not None}"
        )
        print(
            "Cross-Organization disclosure prevented: "
            f"{cross_organization_lookup is None}"
        )
        print(
            "Unknown KnowledgeAsset returns None: "
            f"{missing_asset is None}"
        )
        print(
            "Unknown Organization list rejected: "
            f"{unknown_organization_list_rejected}"
        )
        print(
            "Unknown Organization lookup rejected: "
            f"{unknown_organization_get_rejected}"
        )
        print(
            "Exception hierarchy valid: "
            f"{exception_hierarchy_valid}"
        )
        print(
            "Write methods exposed: "
            f"{bool(exposed_prohibited_methods)}"
        )
        print(
            "Read service committed transaction: "
            f"{persisted_asset_count != 0}"
        )

        print()
        print("Validation: PASSED")
        print(
            "KnowledgeAssetService provides read-only, deterministic, "
            "Organization-scoped Organizational Memory access while "
            "preserving confidentiality, repository boundaries, and "
            "caller-owned transaction state."
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
