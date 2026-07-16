import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.domain.license_status import LicenseStatus
from app.models.license import License
from app.models.organization import Organization
from app.repositories.license_repository import LicenseRepository


def build_license(
    *,
    organization_id: str,
    identifier: str,
    issued_at: datetime,
    status: LicenseStatus,
    payload_hash_character: str,
    supersedes_license_id: str | None = None,
) -> License:
    payload = {
        "license_identifier": identifier,
        "organization_id": organization_id,
        "commercial_edition": (
            CommercialEdition.STARTER.value
        ),
        "commercial_purpose": (
            CommercialPurpose.BETA.value
        ),
        "license_format_version": "1.0",
        "issued_at": issued_at.isoformat(),
    }

    return License(
        organization_id=organization_id,
        license_identifier=identifier,
        status=status.value,
        commercial_edition=(
            CommercialEdition.STARTER.value
        ),
        commercial_purpose=(
            CommercialPurpose.BETA.value
        ),
        license_format_version="1.0",
        issued_at=issued_at,
        effective_at=issued_at,
        expires_at=issued_at + timedelta(days=90),
        seat_limit=10,
        commercial_modules_json=[
            "USOPCore",
        ],
        feature_entitlements_json=[
            "IdentityDecisionPlatform",
        ],
        canonical_payload_json=payload,
        canonical_payload_hash=(
            payload_hash_character * 64
        ),
        signature=(
            f"signature-{identifier}"
        ),
        signing_key_identifier=(
            "repository-regression-key"
        ),
        supersedes_license_id=(
            supersedes_license_id
        ),
        created_by="USOP Repository Regression",
        updated_by="USOP Repository Regression",
    )


def main() -> int:
    print("USOP License Repository Regression")
    print("----------------------------------")

    db = SessionLocal()
    organization_id: str | None = None

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    errors: list[str] = []

    try:
        repository = LicenseRepository(db)

        organization = Organization(
            name="License Repository Regression",
            slug=f"license-repository-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by="USOP Repository Regression",
            updated_by="USOP Repository Regression",
        )

        db.add(organization)
        db.flush()
        db.refresh(organization)

        organization_id = organization.id

        first_license = repository.create(
            build_license(
                organization_id=organization.id,
                identifier=f"first-{suffix}",
                issued_at=now,
                status=LicenseStatus.SUPERSEDED,
                payload_hash_character="a",
            )
        )

        second_license = repository.create(
            build_license(
                organization_id=organization.id,
                identifier=f"second-{suffix}",
                issued_at=now + timedelta(minutes=1),
                status=LicenseStatus.ISSUED,
                payload_hash_character="b",
                supersedes_license_id=first_license.id,
            )
        )

        third_license = repository.create(
            build_license(
                organization_id=organization.id,
                identifier=f"third-{suffix}",
                issued_at=now + timedelta(minutes=2),
                status=LicenseStatus.REVOKED,
                payload_hash_character="c",
                supersedes_license_id=second_license.id,
            )
        )

        by_id = repository.get_by_id(
            second_license.id
        )

        if by_id is None:
            errors.append(
                "License lookup by ID returned no record."
            )
        elif by_id.license_identifier != (
            second_license.license_identifier
        ):
            errors.append(
                "License lookup by ID returned the wrong record."
            )

        by_identifier = repository.get_by_identifier(
            second_license.license_identifier
        )

        if by_identifier is None:
            errors.append(
                "License lookup by identifier returned no record."
            )
        elif by_identifier.id != second_license.id:
            errors.append(
                "License lookup by identifier returned the wrong record."
            )

        latest_issued = (
            repository
            .get_latest_issued_for_organization(
                organization.id
            )
        )

        if latest_issued is None:
            errors.append(
                "Latest issued License lookup returned no record."
            )
        elif latest_issued.id != second_license.id:
            errors.append(
                "Latest issued License lookup incorrectly selected "
                "a Superseded or Revoked record."
            )

        history = (
            repository
            .list_history_for_organization(
                organization.id
            )
        )

        history_ids = [
            item.id
            for item in history
        ]

        expected_history_ids = [
            third_license.id,
            second_license.id,
            first_license.id,
        ]

        if history_ids != expected_history_ids:
            errors.append(
                "License history was not ordered newest first."
            )

        if hasattr(repository, "delete"):
            errors.append(
                "LicenseRepository exposes a prohibited delete operation."
            )

        if hasattr(repository, "update"):
            errors.append(
                "LicenseRepository exposes a prohibited generic update operation."
            )

        # The repository must not commit. A rollback should remove the complete
        # temporary transaction, proving transaction ownership remains external.
        db.rollback()

        persisted_organization = (
            db.query(Organization)
            .filter(
                Organization.id == organization.id,
            )
            .one_or_none()
        )

        persisted_licenses = (
            db.query(License)
            .filter(
                License.organization_id
                == organization.id,
            )
            .count()
        )

        if persisted_organization is not None:
            errors.append(
                "LicenseRepository unexpectedly committed the transaction."
            )

        if persisted_licenses != 0:
            errors.append(
                "LicenseRepository unexpectedly persisted records after rollback."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Organization ID: {organization.id}")
        print(f"Created License count: {len(history)}")
        print(
            "Lookup by ID: "
            f"{by_id is not None}"
        )
        print(
            "Lookup by identifier: "
            f"{by_identifier is not None}"
        )
        print(
            "Latest issued License selected: "
            f"{latest_issued.id == second_license.id}"
        )
        print(
            "History ordered newest first: "
            f"{history_ids == expected_history_ids}"
        )
        print("Generic update exposed: False")
        print("Delete exposed: False")
        print("Repository committed transaction: False")

        print()
        print("Validation: PASSED")
        print(
            "LicenseRepository provides deterministic immutable-record "
            "creation and retrieval while preserving service-layer "
            "transaction ownership and separation from runtime validation."
        )

        return 0

    finally:
        db.rollback()

        if organization_id:
            (
                db.query(License)
                .filter(
                    License.organization_id
                    == organization_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(Organization)
                .filter(
                    Organization.id
                    == organization_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
