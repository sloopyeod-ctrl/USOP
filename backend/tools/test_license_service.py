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
from app.models.audit_event import AuditEvent
from app.models.license import License
from app.models.organization import Organization
from app.schemas.license import (
    LicenseInstallDisposition,
    LicenseInstallRequest,
)
from app.services.license_service import (
    LicenseOrganizationNotFoundError,
    LicenseService,
)


ACTOR = "USOP License Service Regression"


def build_request(
    *,
    organization_id: str,
    identifier: str,
    issued_at: datetime,
    seat_limit: int,
    deployment_identifier: str,
) -> LicenseInstallRequest:
    payload = {
        "organization_id": organization_id,
        "license_identifier": identifier,
        "commercial_edition": (
            CommercialEdition.PROFESSIONAL.value
        ),
        "commercial_purpose": (
            CommercialPurpose.BETA.value
        ),
        "license_format_version": "1.0",
        "issued_at": issued_at.isoformat(),
        "seat_limit": seat_limit,
    }

    return LicenseInstallRequest(
        organization_id=organization_id,
        license_identifier=identifier,
        commercial_edition=(
            CommercialEdition.PROFESSIONAL
        ),
        commercial_purpose=(
            CommercialPurpose.BETA
        ),
        license_format_version="1.0",
        issued_at=issued_at,
        effective_at=issued_at,
        expires_at=issued_at + timedelta(days=90),
        deployment_identifier=deployment_identifier,
        seat_limit=seat_limit,
        commercial_modules=[
            "USOPCore",
        ],
        feature_entitlements=[
            "IdentityDecisionPlatform",
        ],
        canonical_payload=payload,
        canonical_payload_hash="a" * 64,
        signature=f"signature-{identifier}",
        signing_key_identifier=(
            "license-service-regression-key"
        ),
    )


def main() -> int:
    print("USOP Atomic License Service Regression")
    print("--------------------------------------")

    db = SessionLocal()

    suffix = uuid.uuid4().hex
    deployment_identifier = (
        f"deployment-{suffix}"
    )
    now = datetime.now(timezone.utc)

    organization_id: str | None = None
    errors: list[str] = []

    try:
        organization = Organization(
            name="License Service Regression",
            slug=f"license-service-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            deployment_identifier=(
                deployment_identifier
            ),
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        organization_id = organization.id
        service = LicenseService(db)

        first_request = build_request(
            organization_id=organization.id,
            identifier=f"first-{suffix}",
            issued_at=now,
            seat_limit=10,
            deployment_identifier=(
                deployment_identifier
            ),
        )

        first_result = service.install(
            first_request,
            actor=ACTOR,
        )

        if (
            first_result.disposition
            != LicenseInstallDisposition.INSTALLED
        ):
            errors.append(
                "Initial License was not classified as Installed."
            )

        first_audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "License",
                AuditEvent.entity_id
                == first_result.license_id,
                AuditEvent.event_type
                == "LicenseInstalled",
            )
            .count()
        )

        if first_audit_count != 1:
            errors.append(
                "Initial License did not create exactly one audit event."
            )

        duplicate_result = service.install(
            first_request,
            actor=ACTOR,
        )

        if (
            duplicate_result.disposition
            != LicenseInstallDisposition
            .ALREADY_INSTALLED
        ):
            errors.append(
                "Duplicate installation was not idempotent."
            )

        duplicate_audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "License",
                AuditEvent.entity_id
                == first_result.license_id,
                AuditEvent.event_type
                == "LicenseInstalled",
            )
            .count()
        )

        if duplicate_audit_count != 1:
            errors.append(
                "Duplicate installation created another audit event."
            )

        second_request = build_request(
            organization_id=organization.id,
            identifier=f"second-{suffix}",
            issued_at=now + timedelta(minutes=1),
            seat_limit=20,
            deployment_identifier=(
                deployment_identifier
            ),
        )

        second_result = service.install(
            second_request,
            actor=ACTOR,
        )

        first_license = (
            db.query(License)
            .filter(
                License.id
                == first_result.license_id
            )
            .one()
        )

        second_license = (
            db.query(License)
            .filter(
                License.id
                == second_result.license_id
            )
            .one()
        )

        if (
            first_license.status
            != LicenseStatus.SUPERSEDED.value
        ):
            errors.append(
                "Previous License was not marked Superseded."
            )

        if (
            second_license.supersedes_license_id
            != first_license.id
        ):
            errors.append(
                "Replacement License did not preserve supersession lineage."
            )

        if (
            second_result.superseded_license_id
            != first_license.id
        ):
            errors.append(
                "Install result did not identify the superseded License."
            )

        second_audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "License",
                AuditEvent.entity_id
                == second_license.id,
                AuditEvent.event_type
                == "LicenseInstalled",
            )
            .count()
        )

        if second_audit_count != 1:
            errors.append(
                "Replacement License did not create exactly one audit event."
            )

        unknown_rejected = False

        try:
            service.install(
                build_request(
                    organization_id=str(uuid.uuid4()),
                    identifier=f"unknown-{suffix}",
                    issued_at=now,
                    seat_limit=10,
                    deployment_identifier=(
                        deployment_identifier
                    ),
                ),
                actor=ACTOR,
            )
        except LicenseOrganizationNotFoundError:
            unknown_rejected = True

        if not unknown_rejected:
            errors.append(
                "License for an unknown Organization was accepted."
            )

        rollback_request = build_request(
            organization_id=organization.id,
            identifier=f"rollback-{suffix}",
            issued_at=now + timedelta(minutes=2),
            seat_limit=30,
            deployment_identifier=(
                deployment_identifier
            ),
        )

        original_record_pending = (
            service.audit_service.record_pending
        )

        def fail_audit(**kwargs):
            raise RuntimeError(
                "Simulated audit persistence failure."
            )

        service.audit_service.record_pending = fail_audit

        rollback_triggered = False

        try:
            service.install(
                rollback_request,
                actor=ACTOR,
            )
        except RuntimeError:
            rollback_triggered = True
        finally:
            service.audit_service.record_pending = (
                original_record_pending
            )

        rollback_license = (
            db.query(License)
            .filter(
                License.license_identifier
                == rollback_request
                .license_identifier
            )
            .one_or_none()
        )

        second_license_after_failure = (
            db.query(License)
            .filter(
                License.id == second_license.id
            )
            .one()
        )

        if not rollback_triggered:
            errors.append(
                "Simulated audit failure did not propagate."
            )

        if rollback_license is not None:
            errors.append(
                "License remained persisted after audit failure rollback."
            )

        if (
            second_license_after_failure.status
            != LicenseStatus.ISSUED.value
        ):
            errors.append(
                "Previous License supersession was not rolled back "
                "after audit failure."
            )

        license_count = (
            db.query(License)
            .filter(
                License.organization_id
                == organization.id
            )
            .count()
        )

        audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "License",
                AuditEvent.entity_id.in_(
                    [
                        first_license.id,
                        second_license.id,
                    ]
                ),
                AuditEvent.event_type
                == "LicenseInstalled",
            )
            .count()
        )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Organization ID: {organization.id}")
        print(f"Installed License count: {license_count}")
        print(
            "Initial installation: "
            f"{first_result.disposition.value}"
        )
        print(
            "Duplicate installation: "
            f"{duplicate_result.disposition.value}"
        )
        print(
            "Previous License superseded: "
            f"{first_license.status == LicenseStatus.SUPERSEDED.value}"
        )
        print(
            "Supersession lineage preserved: "
            f"{second_license.supersedes_license_id == first_license.id}"
        )
        print(
            "License installation audit events: "
            f"{audit_count}"
        )
        print(
            "Unknown Organization rejected: "
            f"{unknown_rejected}"
        )
        print(
            "Audit failure rolled back License: "
            f"{rollback_license is None}"
        )
        print(
            "Audit failure restored prior status: "
            f"{second_license_after_failure.status == LicenseStatus.ISSUED.value}"
        )
        print(
            "Browser-controlled actor accepted: False"
        )
        print(
            "Cryptographic validity asserted: False"
        )

        print()
        print("Validation: PASSED")
        print(
            "License installation is idempotent, organization-bound, "
            "historically attributable, audited, and atomic across "
            "License persistence, supersession, and audit creation."
        )

        return 0

    finally:
        db.rollback()

        if organization_id:
            license_ids = [
                item[0]
                for item in (
                    db.query(License.id)
                    .filter(
                        License.organization_id
                        == organization_id
                    )
                    .all()
                )
            ]

            if license_ids:
                (
                    db.query(AuditEvent)
                    .filter(
                        AuditEvent.entity_type
                        == "License",
                        AuditEvent.entity_id.in_(
                            license_ids
                        ),
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

                (
                    db.query(License)
                    .filter(
                        License.organization_id
                        == organization_id
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

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
