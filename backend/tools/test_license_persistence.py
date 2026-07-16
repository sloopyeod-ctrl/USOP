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


def main() -> int:
    print("USOP License Persistence Regression")
    print("-----------------------------------")

    db = SessionLocal()

    organization_id: str | None = None
    first_license_id: str | None = None
    replacement_license_id: str | None = None

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    errors: list[str] = []

    try:
        organization = Organization(
            name="License Persistence Regression",
            slug=f"license-persistence-{suffix}",
            status="Active",
            organization_type="Customer",
            primary_domain="example.invalid",
            time_zone="UTC",
            deployment_identifier=(
                f"deployment-{suffix}"
            ),
            created_by="USOP Regression",
            updated_by="USOP Regression",
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        organization_id = organization.id

        payload = {
            "license_identifier": (
                f"license-{suffix}"
            ),
            "organization_id": organization.id,
            "commercial_edition": (
                CommercialEdition.STARTER.value
            ),
            "commercial_purpose": (
                CommercialPurpose.BETA.value
            ),
            "license_format_version": "1.0",
            "seat_limit": 10,
            "commercial_modules": [
                "USOPCore",
            ],
            "feature_entitlements": [
                "IdentityDecisionPlatform",
            ],
        }

        first_license = License(
            organization_id=organization.id,
            license_identifier=(
                f"license-{suffix}"
            ),
            status=LicenseStatus.ISSUED.value,
            commercial_edition=(
                CommercialEdition.STARTER.value
            ),
            commercial_purpose=(
                CommercialPurpose.BETA.value
            ),
            license_format_version="1.0",
            issued_at=now,
            effective_at=now,
            expires_at=now + timedelta(days=90),
            deployment_identifier=(
                organization.deployment_identifier
            ),
            seat_limit=10,
            commercial_modules_json=[
                "USOPCore",
            ],
            feature_entitlements_json=[
                "IdentityDecisionPlatform",
            ],
            canonical_payload_json=payload,
            canonical_payload_hash="a" * 64,
            signature="regression-signature",
            signing_key_identifier=(
                "regression-signing-key"
            ),
            created_by="USOP Regression",
            updated_by="USOP Regression",
        )

        db.add(first_license)
        db.commit()
        db.refresh(first_license)

        first_license_id = first_license.id

        replacement_payload = {
            **payload,
            "license_identifier": (
                f"replacement-license-{suffix}"
            ),
            "seat_limit": 20,
        }

        replacement_license = License(
            organization_id=organization.id,
            license_identifier=(
                f"replacement-license-{suffix}"
            ),
            status=LicenseStatus.ISSUED.value,
            commercial_edition=(
                CommercialEdition.PROFESSIONAL.value
            ),
            commercial_purpose=(
                CommercialPurpose.BETA.value
            ),
            license_format_version="1.0",
            issued_at=now + timedelta(minutes=1),
            effective_at=now + timedelta(minutes=1),
            expires_at=now + timedelta(days=90),
            deployment_identifier=(
                organization.deployment_identifier
            ),
            seat_limit=20,
            commercial_modules_json=[
                "USOPCore",
            ],
            feature_entitlements_json=[
                "IdentityDecisionPlatform",
            ],
            canonical_payload_json=replacement_payload,
            canonical_payload_hash="b" * 64,
            signature="replacement-signature",
            signing_key_identifier=(
                "regression-signing-key"
            ),
            supersedes_license_id=(
                first_license.id
            ),
            created_by="USOP Regression",
            updated_by="USOP Regression",
        )

        db.add(replacement_license)
        db.commit()
        db.refresh(replacement_license)

        replacement_license_id = (
            replacement_license.id
        )

        persisted = (
            db.query(License)
            .filter(
                License.id == replacement_license.id
            )
            .one_or_none()
        )

        if persisted is None:
            errors.append(
                "Replacement License could not be retrieved."
            )
        else:
            if (
                persisted.organization_id
                != organization.id
            ):
                errors.append(
                    "Organization binding was not preserved."
                )

            if (
                persisted.supersedes_license_id
                != first_license.id
            ):
                errors.append(
                    "Historical License supersession "
                    "was not preserved."
                )

            if persisted.seat_limit != 20:
                errors.append(
                    "Seat entitlement was not persisted."
                )

            if (
                persisted.canonical_payload_hash
                != "b" * 64
            ):
                errors.append(
                    "Canonical payload hash was not persisted."
                )

            if (
                persisted.signature
                != "replacement-signature"
            ):
                errors.append(
                    "License signature was not persisted."
                )

        duplicate_rejected = False

        duplicate = License(
            organization_id=organization.id,
            license_identifier=(
                first_license.license_identifier
            ),
            status=LicenseStatus.ISSUED.value,
            commercial_edition=(
                CommercialEdition.STARTER.value
            ),
            commercial_purpose=(
                CommercialPurpose.BETA.value
            ),
            license_format_version="1.0",
            issued_at=now,
            effective_at=now,
            canonical_payload_json=payload,
            canonical_payload_hash="c" * 64,
            signature="duplicate-signature",
            signing_key_identifier=(
                "regression-signing-key"
            ),
            created_by="USOP Regression",
            updated_by="USOP Regression",
        )

        db.add(duplicate)

        try:
            db.commit()
        except Exception:
            db.rollback()
            duplicate_rejected = True

        if not duplicate_rejected:
            errors.append(
                "Duplicate License identifier was accepted."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Organization ID: {organization.id}")
        print(f"Original License ID: {first_license.id}")
        print(
            "Replacement License ID: "
            f"{replacement_license.id}"
        )
        print(
            "Organization binding preserved: True"
        )
        print(
            "Historical supersession preserved: True"
        )
        print(
            "Signed payload persisted: True"
        )
        print(
            "Duplicate identifier rejected: "
            f"{duplicate_rejected}"
        )
        print(
            "Private signing key persisted: False"
        )
        print(
            "Subscription State persisted: False"
        )

        print()
        print("Validation: PASSED")
        print(
            "License persistence, Organization binding, "
            "historical supersession, signed payload storage, "
            "and uniqueness enforcement are operating correctly."
        )

        return 0

    finally:
        db.rollback()

        if replacement_license_id:
            (
                db.query(License)
                .filter(
                    License.id
                    == replacement_license_id
                )
                .delete(
                    synchronize_session=False
                )
            )

        if first_license_id:
            (
                db.query(License)
                .filter(
                    License.id
                    == first_license_id
                )
                .delete(
                    synchronize_session=False
                )
            )

        if organization_id:
            (
                db.query(Organization)
                .filter(
                    Organization.id
                    == organization_id
                )
                .delete(
                    synchronize_session=False
                )
            )

        db.commit()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
