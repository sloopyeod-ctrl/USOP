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
    KnowledgeAssetOrganizationNotFoundError,
    KnowledgeAssetService,
    KnowledgeAssetValidationError,
)


ACTOR = "USOP Knowledge Asset Pending Creation Regression"


def main() -> int:
    print("USOP Knowledge Asset Pending Creation Regression")
    print("-----------------------------------------------")

    db = SessionLocal()
    service = KnowledgeAssetService(db)

    suffix = uuid.uuid4().hex

    primary_organization_id: str | None = None
    secondary_organization_id: str | None = None

    errors: list[str] = []

    try:
        primary_organization = Organization(
            name="Knowledge Asset Creation Primary",
            slug=f"knowledge-asset-creation-primary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_organization = Organization(
            name="Knowledge Asset Creation Secondary",
            slug=f"knowledge-asset-creation-secondary-{suffix}",
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

        first_asset = service.create_pending(
            organization_id=primary_organization.id,
            title="  Privileged Identity Management Policy  ",
            summary="  Controls privileged role eligibility.  ",
            guidance="  Require approval, MFA, and time limits.  ",
            category=KnowledgeCategory.AUTHORIZATION,
            status=KnowledgeAssetStatus.DRAFT,
            source_system="  USOP  ",
            source_identifier="  pim-policy  ",
            confidence_score=95,
            actor=ACTOR,
        )

        second_asset = service.create_pending(
            organization_id=primary_organization.id,
            title="Privileged Identity Management Policy",
            summary=None,
            guidance="Review and approve the revised guidance.",
            category=KnowledgeCategory.AUTHORIZATION.value,
            status=KnowledgeAssetStatus.UNDER_REVIEW.value,
            confidence_score=100,
            actor=ACTOR,
        )

        secondary_asset = service.create_pending(
            organization_id=secondary_organization.id,
            title="Privileged Identity Management Policy",
            guidance="Secondary Organization guidance.",
            category=KnowledgeCategory.AUTHORIZATION,
            actor=ACTOR,
        )

        if first_asset.version != 1:
            errors.append(
                "The first KnowledgeAsset version was not 1."
            )

        if second_asset.version != 2:
            errors.append(
                "The second KnowledgeAsset version was not 2."
            )

        if secondary_asset.version != 1:
            errors.append(
                "Version allocation crossed the Organization boundary."
            )

        if first_asset.title != (
            "Privileged Identity Management Policy"
        ):
            errors.append(
                "KnowledgeAsset title was not normalized."
            )

        if first_asset.summary != (
            "Controls privileged role eligibility."
        ):
            errors.append(
                "KnowledgeAsset summary was not normalized."
            )

        if first_asset.guidance != (
            "Require approval, MFA, and time limits."
        ):
            errors.append(
                "KnowledgeAsset guidance was not normalized."
            )

        if first_asset.source_system != "USOP":
            errors.append(
                "KnowledgeAsset source system was not normalized."
            )

        if first_asset.source_identifier != "pim-policy":
            errors.append(
                "KnowledgeAsset source identifier was not normalized."
            )

        if first_asset.category != (
            KnowledgeCategory.AUTHORIZATION.value
        ):
            errors.append(
                "KnowledgeAsset category was not persisted canonically."
            )

        if second_asset.status != (
            KnowledgeAssetStatus.UNDER_REVIEW.value
        ):
            errors.append(
                "KnowledgeAsset status was not persisted canonically."
            )

        validation_cases = [
            {
                "name": "blank title",
                "arguments": {
                    "title": "   ",
                    "guidance": "Valid guidance",
                    "category": KnowledgeCategory.CLOUD,
                },
            },
            {
                "name": "blank guidance",
                "arguments": {
                    "title": "Valid title",
                    "guidance": "   ",
                    "category": KnowledgeCategory.CLOUD,
                },
            },
            {
                "name": "unknown category",
                "arguments": {
                    "title": "Valid title",
                    "guidance": "Valid guidance",
                    "category": "NotARealCategory",
                },
            },
            {
                "name": "unknown status",
                "arguments": {
                    "title": "Valid title",
                    "guidance": "Valid guidance",
                    "category": KnowledgeCategory.CLOUD,
                    "status": "NotARealStatus",
                },
            },
            {
                "name": "invalid confidence",
                "arguments": {
                    "title": "Valid title",
                    "guidance": "Valid guidance",
                    "category": KnowledgeCategory.CLOUD,
                    "confidence_score": 101,
                },
            },
        ]

        rejected_validation_cases: list[str] = []

        for validation_case in validation_cases:
            try:
                service.create_pending(
                    organization_id=primary_organization.id,
                    actor=ACTOR,
                    **validation_case["arguments"],
                )
            except KnowledgeAssetValidationError:
                rejected_validation_cases.append(
                    validation_case["name"]
                )

        expected_rejected_cases = {
            validation_case["name"]
            for validation_case in validation_cases
        }

        if set(rejected_validation_cases) != (
            expected_rejected_cases
        ):
            errors.append(
                "One or more invalid KnowledgeAsset inputs "
                "were not rejected."
            )

        unknown_organization_rejected = False

        try:
            service.create_pending(
                organization_id=str(uuid.uuid4()),
                title="Unknown Organization Asset",
                guidance="This must not be created.",
                category=KnowledgeCategory.COMPLIANCE,
                actor=ACTOR,
            )
        except KnowledgeAssetOrganizationNotFoundError:
            unknown_organization_rejected = True

        if not unknown_organization_rejected:
            errors.append(
                "Unknown Organization creation was not rejected."
            )

        if not hasattr(service, "create"):
            errors.append(
                "KnowledgeAssetService exposes an unintended "
                "public create() method."
            )

        if hasattr(service, "commit"):
            errors.append(
                "KnowledgeAssetService exposes commit()."
            )

        if hasattr(service, "rollback"):
            errors.append(
                "KnowledgeAssetService exposes rollback()."
            )

        created_asset_ids = [
            first_asset.id,
            second_asset.id,
            secondary_asset.id,
        ]

        db.rollback()

        persisted_asset_count = (
            db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.id.in_(
                    created_asset_ids
                )
            )
            .count()
        )

        persisted_organization_count = (
            db.query(Organization)
            .filter(
                Organization.id.in_(
                    [
                        primary_organization.id,
                        secondary_organization.id,
                    ]
                )
            )
            .count()
        )

        if persisted_asset_count != 0:
            errors.append(
                "create_pending() unexpectedly committed "
                "KnowledgeAsset records."
            )

        if persisted_organization_count != 0:
            errors.append(
                "create_pending() unexpectedly committed "
                "the caller-owned transaction."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Primary first version: {first_asset.version}")
        print(f"Primary second version: {second_asset.version}")
        print(
            "Secondary Organization first version: "
            f"{secondary_asset.version}"
        )
        print(
            "Title normalized: "
            f"{first_asset.title == 'Privileged Identity Management Policy'}"
        )
        print(
            "Category canonical: "
            f"{first_asset.category == KnowledgeCategory.AUTHORIZATION.value}"
        )
        print(
            "Status canonical: "
            f"{second_asset.status == KnowledgeAssetStatus.UNDER_REVIEW.value}"
        )
        print(
            "Invalid input cases rejected: "
            f"{len(rejected_validation_cases)}"
        )
        print(
            "Unknown Organization rejected: "
            f"{unknown_organization_rejected}"
        )
        print(
            "Public create() available: "
            f"{hasattr(service, 'create')}"
        )
        print(
            "Pending creation committed transaction: "
            f"{persisted_asset_count != 0}"
        )

        print()
        print("Validation: PASSED")
        print(
            "KnowledgeAssetService.create_pending() validates and "
            "normalizes Organizational Memory, allocates versions within "
            "the Organization boundary, and preserves caller-owned "
            "transaction control."
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
