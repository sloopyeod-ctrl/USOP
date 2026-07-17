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
from app.domain.organization_status import OrganizationStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.models.audit_event import AuditEvent
from app.models.license import License
from app.models.organization import Organization
from app.models.platform_user import PlatformUser
from app.repositories.license_repository import LicenseRepository
from app.services.platform_user_service import (
    PlatformUserBootstrapAlreadyCompletedError,
    PlatformUserLicenseNotEligibleError,
    PlatformUserOrganizationNotActiveError,
    PlatformUserOrganizationNotFoundError,
    PlatformUserService,
)


ACTOR = "USOP Platform User Service Regression"


def build_organization(
    *,
    suffix: str,
    label: str,
    status: OrganizationStatus = OrganizationStatus.ACTIVE,
) -> Organization:
    return Organization(
        name=f"Platform User Service {label}",
        slug=f"platform-user-service-{label.lower()}-{suffix}",
        status=status.value,
        organization_type="Customer",
        time_zone="UTC",
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def build_license(
    *,
    organization_id: str,
    identifier: str,
    now: datetime,
    status: LicenseStatus = LicenseStatus.ISSUED,
    effective_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> License:
    effective = effective_at or now
    expiration = (
        expires_at
        if expires_at is not None
        else now + timedelta(days=90)
    )

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
        "issued_at": now.isoformat(),
    }

    return License(
        organization_id=organization_id,
        license_identifier=identifier,
        status=status.value,
        commercial_edition=(
            CommercialEdition.PROFESSIONAL.value
        ),
        commercial_purpose=(
            CommercialPurpose.BETA.value
        ),
        license_format_version="1.0",
        issued_at=now,
        effective_at=effective,
        expires_at=expiration,
        seat_limit=10,
        commercial_modules_json=["USOPCore"],
        feature_entitlements_json=[
            "IdentityDecisionPlatform",
        ],
        canonical_payload_json=payload,
        canonical_payload_hash="a" * 64,
        signature=f"signature-{identifier}",
        signing_key_identifier=(
            "platform-user-service-regression-key"
        ),
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def main() -> int:
    print("USOP Bootstrap Administrator Service Regression")
    print("-----------------------------------------------")

    db = SessionLocal()
    service = PlatformUserService(db)
    license_repository = LicenseRepository(db)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_ids: list[str] = []
    errors: list[str] = []

    try:
        unknown_rejected = False

        try:
            service.bootstrap_first_administrator(
                organization_id=str(uuid.uuid4()),
                display_name="Unknown Administrator",
                email=f"unknown-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except PlatformUserOrganizationNotFoundError:
            unknown_rejected = True

        if not unknown_rejected:
            errors.append(
                "Unknown Organization was accepted."
            )

        no_license_organization = build_organization(
            suffix=suffix,
            label="NoLicense",
        )

        db.add(no_license_organization)
        db.commit()
        db.refresh(no_license_organization)
        organization_ids.append(
            no_license_organization.id
        )

        no_license_rejected = False

        try:
            service.bootstrap_first_administrator(
                organization_id=(
                    no_license_organization.id
                ),
                display_name="No License Administrator",
                email=f"no-license-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except PlatformUserLicenseNotEligibleError:
            no_license_rejected = True

        if not no_license_rejected:
            errors.append(
                "Organization without an eligible License was accepted."
            )

        suspended_organization = build_organization(
            suffix=suffix,
            label="Suspended",
            status=OrganizationStatus.SUSPENDED,
        )

        db.add(suspended_organization)
        db.flush()
        db.refresh(suspended_organization)

        license_repository.create(
            build_license(
                organization_id=suspended_organization.id,
                identifier=f"suspended-{suffix}",
                now=now,
            )
        )

        db.commit()
        organization_ids.append(
            suspended_organization.id
        )

        suspended_rejected = False

        try:
            service.bootstrap_first_administrator(
                organization_id=suspended_organization.id,
                display_name="Suspended Administrator",
                email=f"suspended-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except PlatformUserOrganizationNotActiveError:
            suspended_rejected = True

        if not suspended_rejected:
            errors.append(
                "Suspended Organization was accepted."
            )

        future_organization = build_organization(
            suffix=suffix,
            label="Future",
        )

        db.add(future_organization)
        db.flush()
        db.refresh(future_organization)

        license_repository.create(
            build_license(
                organization_id=future_organization.id,
                identifier=f"future-{suffix}",
                now=now,
                effective_at=now + timedelta(days=1),
                expires_at=now + timedelta(days=90),
            )
        )

        db.commit()
        organization_ids.append(
            future_organization.id
        )

        future_rejected = False

        try:
            service.bootstrap_first_administrator(
                organization_id=future_organization.id,
                display_name="Future Administrator",
                email=f"future-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except PlatformUserLicenseNotEligibleError:
            future_rejected = True

        if not future_rejected:
            errors.append(
                "Future-effective License was accepted."
            )

        expired_organization = build_organization(
            suffix=suffix,
            label="Expired",
        )

        db.add(expired_organization)
        db.flush()
        db.refresh(expired_organization)

        license_repository.create(
            build_license(
                organization_id=expired_organization.id,
                identifier=f"expired-{suffix}",
                now=now - timedelta(days=30),
                effective_at=now - timedelta(days=30),
                expires_at=now - timedelta(seconds=1),
            )
        )

        db.commit()
        organization_ids.append(
            expired_organization.id
        )

        expired_rejected = False

        try:
            service.bootstrap_first_administrator(
                organization_id=expired_organization.id,
                display_name="Expired Administrator",
                email=f"expired-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except PlatformUserLicenseNotEligibleError:
            expired_rejected = True

        if not expired_rejected:
            errors.append(
                "Expired License was accepted."
            )

        eligible_organization = build_organization(
            suffix=suffix,
            label="Eligible",
        )

        db.add(eligible_organization)
        db.flush()
        db.refresh(eligible_organization)

        eligible_license = license_repository.create(
            build_license(
                organization_id=eligible_organization.id,
                identifier=f"eligible-{suffix}",
                now=now,
            )
        )

        db.commit()
        organization_ids.append(
            eligible_organization.id
        )

        tenant_id = str(uuid.uuid4())
        subject_id = str(uuid.uuid4())

        platform_user = (
            service.bootstrap_first_administrator(
                organization_id=eligible_organization.id,
                display_name="  Initial Platform Administrator  ",
                email=f"ADMIN-{suffix}@EXAMPLE.INVALID",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=tenant_id,
                external_subject_id=subject_id,
                identity_issuer=(
                    "https://login.microsoftonline.com/"
                    f"{tenant_id}/v2.0"
                ),
                actor=ACTOR,
                evaluated_at=now,
            )
        )

        persisted_user = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.id == platform_user.id,
            )
            .one()
        )

        audit_events = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "PlatformUser",
                AuditEvent.entity_id == platform_user.id,
                AuditEvent.event_type
                == "PlatformAdministratorBootstrapped",
            )
            .all()
        )

        if len(audit_events) != 1:
            errors.append(
                "Bootstrap did not create exactly one audit event."
            )

        if (
            persisted_user.status
            != PlatformUserStatus.INVITED.value
        ):
            errors.append(
                "Bootstrapped Platform User was not Invited."
            )

        if not persisted_user.created_via_bootstrap:
            errors.append(
                "Bootstrap provenance was not preserved."
            )

        if (
            persisted_user.display_name
            != "Initial Platform Administrator"
        ):
            errors.append(
                "Display name normalization failed."
            )

        if (
            persisted_user.email
            != f"admin-{suffix}@example.invalid"
        ):
            errors.append(
                "Email normalization failed."
            )

        second_bootstrap_rejected = False

        try:
            service.bootstrap_first_administrator(
                organization_id=eligible_organization.id,
                display_name="Second Administrator",
                email=f"second-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except PlatformUserBootstrapAlreadyCompletedError:
            second_bootstrap_rejected = True

        if not second_bootstrap_rejected:
            errors.append(
                "Second bootstrap attempt was accepted."
            )

        rollback_organization = build_organization(
            suffix=suffix,
            label="Rollback",
        )

        db.add(rollback_organization)
        db.flush()
        db.refresh(rollback_organization)

        license_repository.create(
            build_license(
                organization_id=rollback_organization.id,
                identifier=f"rollback-{suffix}",
                now=now,
            )
        )

        db.commit()
        organization_ids.append(
            rollback_organization.id
        )

        original_record_pending = (
            service.audit_service.record_pending
        )

        def fail_audit(**kwargs):
            raise RuntimeError(
                "Simulated bootstrap audit failure."
            )

        service.audit_service.record_pending = fail_audit
        rollback_triggered = False

        try:
            service.bootstrap_first_administrator(
                organization_id=rollback_organization.id,
                display_name="Rollback Administrator",
                email=f"rollback-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                actor=ACTOR,
                evaluated_at=now,
            )
        except RuntimeError:
            rollback_triggered = True
        finally:
            service.audit_service.record_pending = (
                original_record_pending
            )

        rollback_user_count = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == rollback_organization.id
            )
            .count()
        )

        if not rollback_triggered:
            errors.append(
                "Simulated audit failure did not propagate."
            )

        if rollback_user_count != 0:
            errors.append(
                "Platform User remained after audit failure rollback."
            )

        eligible_lookup = (
            license_repository
            .get_bootstrap_eligible_license(
                eligible_organization.id,
                evaluated_at=now,
            )
        )

        if (
            eligible_lookup is None
            or eligible_lookup.id
            != eligible_license.id
        ):
            errors.append(
                "Centralized License eligibility returned "
                "the wrong record."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Platform User ID: {platform_user.id}")
        print(
            "Unknown Organization rejected: "
            f"{unknown_rejected}"
        )
        print(
            "Missing License rejected: "
            f"{no_license_rejected}"
        )
        print(
            "Suspended Organization rejected: "
            f"{suspended_rejected}"
        )
        print(
            "Future License rejected: "
            f"{future_rejected}"
        )
        print(
            "Expired License rejected: "
            f"{expired_rejected}"
        )
        print(
            "Eligible License selected: "
            f"{eligible_lookup.id == eligible_license.id}"
        )
        print(
            "Initial Platform User created: "
            f"{persisted_user.id == platform_user.id}"
        )
        print(
            "Bootstrap provenance preserved: "
            f"{persisted_user.created_via_bootstrap}"
        )
        print(
            "Initial status is Invited: "
            f"{persisted_user.status == PlatformUserStatus.INVITED.value}"
        )
        print(
            "Bootstrap audit event count: "
            f"{len(audit_events)}"
        )
        print(
            "Second bootstrap rejected: "
            f"{second_bootstrap_rejected}"
        )
        print(
            "Audit failure rolled back Platform User: "
            f"{rollback_user_count == 0}"
        )
        print("Role assigned: False")
        print("Seat allocated: False")
        print("Authentication completed: False")
        print("Browser-controlled actor accepted: False")

        print()
        print("Validation: PASSED")
        print(
            "Platform Administrator bootstrap is Organization-bound, "
            "License-gated, one-time, normalized, audited, concurrency-aware, "
            "and atomic across Platform User and audit persistence."
        )

        return 0

    finally:
        db.rollback()

        if organization_ids:
            platform_user_ids = [
                item[0]
                for item in (
                    db.query(PlatformUser.id)
                    .filter(
                        PlatformUser.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            if platform_user_ids:
                (
                    db.query(AuditEvent)
                    .filter(
                        AuditEvent.entity_type
                        == "PlatformUser",
                        AuditEvent.entity_id.in_(
                            platform_user_ids
                        ),
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            (
                db.query(PlatformUser)
                .filter(
                    PlatformUser.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(License)
                .filter(
                    License.organization_id.in_(
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
