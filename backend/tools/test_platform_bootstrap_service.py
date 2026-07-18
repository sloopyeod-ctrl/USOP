import inspect
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
from app.models.platform_permission import PlatformPermission
from app.models.platform_role import PlatformRole
from app.models.platform_role_assignment import (
    PlatformRoleAssignment,
)
from app.models.platform_role_permission import (
    PlatformRolePermission,
)
from app.models.platform_user import PlatformUser
from app.repositories.license_repository import LicenseRepository
from app.services import platform_bootstrap_service as bootstrap_module
from app.services.platform_bootstrap_service import (
    PLATFORM_ADMINISTRATION_ACTION,
    PLATFORM_ADMINISTRATION_PERMISSION_KEY,
    PLATFORM_ADMINISTRATION_RESOURCE,
    PLATFORM_ADMINISTRATOR_ROLE_KEY,
    SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
    PlatformBootstrapService,
)
from app.services.platform_authorization_service import (
    SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
)
from app.services.platform_user_service import (
    PlatformUserBootstrapAlreadyCompletedError,
)


ACTOR = "USOP Platform Bootstrap Service Regression"


def build_organization(
    *,
    suffix: str,
    label: str,
) -> Organization:
    return Organization(
        name=f"Platform Bootstrap {label}",
        slug=f"platform-bootstrap-{label.lower()}-{suffix}",
        status=OrganizationStatus.ACTIVE.value,
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
) -> License:
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
        status=LicenseStatus.ISSUED.value,
        commercial_edition=(
            CommercialEdition.PROFESSIONAL.value
        ),
        commercial_purpose=(
            CommercialPurpose.BETA.value
        ),
        license_format_version="1.0",
        issued_at=now,
        effective_at=now,
        expires_at=now + timedelta(days=90),
        seat_limit=10,
        commercial_modules_json=["USOPCore"],
        feature_entitlements_json=[
            "IdentityDecisionPlatform",
        ],
        canonical_payload_json=payload,
        canonical_payload_hash="b" * 64,
        signature=f"signature-{identifier}",
        signing_key_identifier=(
            "platform-bootstrap-regression-key"
        ),
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def print_phase(
    number: int,
    title: str,
) -> None:
    print()
    print(f"Phase {number}: {title}")
    print("-" * (9 + len(title)))


def print_check(
    label: str,
    passed: bool,
) -> None:
    result = "PASS" if passed else "FAIL"
    print(f"{label:.<44} {result}")


def main() -> int:
    print("USOP Platform Bootstrap Service Regression")
    print("=" * 42)

    db = SessionLocal()
    service = PlatformBootstrapService(db)
    license_repository = LicenseRepository(db)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_ids: list[str] = []
    created_permission_ids: list[str] = []
    errors: list[str] = []

    original_role_key = (
        bootstrap_module.PLATFORM_ADMINISTRATOR_ROLE_KEY
    )
    original_permission_key = (
        bootstrap_module.PLATFORM_ADMINISTRATION_PERMISSION_KEY
    )
    original_resource = (
        bootstrap_module.PLATFORM_ADMINISTRATION_RESOURCE
    )
    original_action = (
        bootstrap_module.PLATFORM_ADMINISTRATION_ACTION
    )

    try:
        print_phase(1, "Environment")

        rollback_organization = build_organization(
            suffix=suffix,
            label="Rollback",
        )

        happy_organization = build_organization(
            suffix=suffix,
            label="HappyPath",
        )

        db.add_all(
            [
                rollback_organization,
                happy_organization,
            ]
        )
        db.flush()

        db.refresh(rollback_organization)
        db.refresh(happy_organization)

        organization_ids.extend(
            [
                rollback_organization.id,
                happy_organization.id,
            ]
        )

        rollback_license = license_repository.create(
            build_license(
                organization_id=rollback_organization.id,
                identifier=f"rollback-{suffix}",
                now=now,
            )
        )

        happy_license = license_repository.create(
            build_license(
                organization_id=happy_organization.id,
                identifier=f"happy-{suffix}",
                now=now,
            )
        )

        db.commit()

        environment_ready = all(
            [
                rollback_organization.id,
                happy_organization.id,
                rollback_license.id,
                happy_license.id,
            ]
        )

        if not environment_ready:
            errors.append(
                "Regression environment was not created."
            )

        print_check(
            "Environment ready",
            bool(environment_ready),
        )

        print_phase(2, "Atomic Rollback")

        rollback_role_key = (
            f"platform-administrator-rollback-{suffix}"
        )
        rollback_permission_key = (
            f"platform-administration.rollback-{suffix}"
        )
        rollback_resource = (
            f"platform-administration-rollback-{suffix}"
        )
        rollback_action = (
            f"manage-rollback-{suffix}"
        )

        bootstrap_module.PLATFORM_ADMINISTRATOR_ROLE_KEY = (
            rollback_role_key
        )
        bootstrap_module.PLATFORM_ADMINISTRATION_PERMISSION_KEY = (
            rollback_permission_key
        )
        bootstrap_module.PLATFORM_ADMINISTRATION_RESOURCE = (
            rollback_resource
        )
        bootstrap_module.PLATFORM_ADMINISTRATION_ACTION = (
            rollback_action
        )

        original_completion_audit = (
            service.audit_service.record_pending
        )

        def fail_completion_audit(**kwargs):
            if (
                kwargs.get("event_type")
                == "PlatformBootstrapCompleted"
            ):
                raise RuntimeError(
                    "Simulated final bootstrap audit failure."
                )

            return original_completion_audit(**kwargs)

        service.audit_service.record_pending = (
            fail_completion_audit
        )

        rollback_failure_propagated = False

        try:
            service.bootstrap_platform_administrator(
                organization_id=rollback_organization.id,
                display_name="Rollback Administrator",
                email=f"rollback-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                evaluated_at=now,
            )
        except RuntimeError as error:
            if (
                str(error)
                == "Simulated final bootstrap audit failure."
            ):
                rollback_failure_propagated = True
            else:
                raise
        finally:
            service.audit_service.record_pending = (
                original_completion_audit
            )

            bootstrap_module.PLATFORM_ADMINISTRATOR_ROLE_KEY = (
                original_role_key
            )
            bootstrap_module.PLATFORM_ADMINISTRATION_PERMISSION_KEY = (
                original_permission_key
            )
            bootstrap_module.PLATFORM_ADMINISTRATION_RESOURCE = (
                original_resource
            )
            bootstrap_module.PLATFORM_ADMINISTRATION_ACTION = (
                original_action
            )

        rollback_user_count = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == rollback_organization.id
            )
            .count()
        )

        rollback_role_count = (
            db.query(PlatformRole)
            .filter(
                PlatformRole.organization_id
                == rollback_organization.id
            )
            .count()
        )

        rollback_permission_count = (
            db.query(PlatformPermission)
            .filter(
                PlatformPermission.permission_key
                == rollback_permission_key
            )
            .count()
        )

        rollback_mapping_count = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == rollback_organization.id
            )
            .count()
        )

        rollback_assignment_count = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == rollback_organization.id
            )
            .count()
        )

        rollback_audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.metadata_json["organization_id"]
                .as_string()
                == rollback_organization.id
            )
            .count()
        )

        rollback_checks = {
            "Failure propagated": (
                rollback_failure_propagated
            ),
            "Platform User rolled back": (
                rollback_user_count == 0
            ),
            "Platform Role rolled back": (
                rollback_role_count == 0
            ),
            "Platform Permission rolled back": (
                rollback_permission_count == 0
            ),
            "Permission mapping rolled back": (
                rollback_mapping_count == 0
            ),
            "Role assignment rolled back": (
                rollback_assignment_count == 0
            ),
            "Audit events rolled back": (
                rollback_audit_count == 0
            ),
        }

        for label, passed in rollback_checks.items():
            print_check(label, passed)

            if not passed:
                errors.append(
                    f"Atomic rollback check failed: {label}."
                )

        print_phase(3, "Happy Path")

        result = service.bootstrap_platform_administrator(
            organization_id=happy_organization.id,
            display_name="Initial Platform Administrator",
            email=f"administrator-{suffix}@example.invalid",
            identity_provider="MicrosoftEntraID",
            external_tenant_id=str(uuid.uuid4()),
            external_subject_id=str(uuid.uuid4()),
            identity_issuer=(
                "https://login.microsoftonline.us/"
            ),
            evaluated_at=now,
        )

        created_permission_ids.append(
            result.platform_permission_id
        )

        persisted_user = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.id
                == result.platform_user_id
            )
            .one_or_none()
        )

        persisted_role = (
            db.query(PlatformRole)
            .filter(
                PlatformRole.id
                == result.platform_role_id
            )
            .one_or_none()
        )

        persisted_permission = (
            db.query(PlatformPermission)
            .filter(
                PlatformPermission.id
                == result.platform_permission_id
            )
            .one_or_none()
        )

        persisted_mapping = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.id
                == result.role_permission_mapping_id
            )
            .one_or_none()
        )

        persisted_assignment = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.id
                == result.role_assignment_id
            )
            .one_or_none()
        )

        completion_audit = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.event_type
                == "PlatformBootstrapCompleted",
                AuditEvent.entity_type
                == "Organization",
                AuditEvent.entity_id
                == happy_organization.id,
            )
            .one_or_none()
        )

        happy_checks = {
            "Platform User created": (
                persisted_user is not None
            ),
            "Platform Role created": (
                persisted_role is not None
            ),
            "Platform Permission created": (
                persisted_permission is not None
            ),
            "Permission mapping created": (
                persisted_mapping is not None
            ),
            "Role assignment created": (
                persisted_assignment is not None
            ),
            "Completion audit created": (
                completion_audit is not None
            ),
        }

        for label, passed in happy_checks.items():
            print_check(label, passed)

            if not passed:
                errors.append(
                    f"Happy-path persistence failed: {label}."
                )

        print_phase(4, "Database Contract")

        organization_user_count = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == happy_organization.id
            )
            .count()
        )

        organization_role_count = (
            db.query(PlatformRole)
            .filter(
                PlatformRole.organization_id
                == happy_organization.id
            )
            .count()
        )

        organization_mapping_count = (
            db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == happy_organization.id
            )
            .count()
        )

        organization_assignment_count = (
            db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == happy_organization.id
            )
            .count()
        )

        bootstrap_audit_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.id.in_(
                    result.audit_event_ids
                )
            )
            .count()
        )

        database_checks = {
            "Exactly one Platform User": (
                organization_user_count == 1
            ),
            "Exactly one Platform Role": (
                organization_role_count == 1
            ),
            "Exactly one permission mapping": (
                organization_mapping_count == 1
            ),
            "Exactly one role assignment": (
                organization_assignment_count == 1
            ),
            "All returned audit events persisted": (
                bootstrap_audit_count
                == len(result.audit_event_ids)
            ),
            "Eligible License returned": (
                result.license_id == happy_license.id
            ),
        }

        for label, passed in database_checks.items():
            print_check(label, passed)

            if not passed:
                errors.append(
                    f"Database contract failed: {label}."
                )

        print_phase(5, "One-Time Bootstrap")

        second_bootstrap_rejected = False

        try:
            service.bootstrap_platform_administrator(
                organization_id=happy_organization.id,
                display_name="Second Administrator",
                email=f"second-{suffix}@example.invalid",
                identity_provider="MicrosoftEntraID",
                external_tenant_id=str(uuid.uuid4()),
                external_subject_id=str(uuid.uuid4()),
                evaluated_at=now,
            )
        except PlatformUserBootstrapAlreadyCompletedError:
            second_bootstrap_rejected = True

        print_check(
            "Second bootstrap rejected",
            second_bootstrap_rejected,
        )

        if not second_bootstrap_rejected:
            errors.append(
                "Second Platform Administrator bootstrap "
                "was accepted."
            )

        print_phase(6, "Security Contract")

        signature = inspect.signature(
            service.bootstrap_platform_administrator
        )

        prohibited_parameters = {
            "actor",
            "platform_role_id",
            "platform_permission_id",
            "role_key",
            "permission_key",
            "authorization_granted",
            "seat_allocated",
            "authentication_completed",
        }

        exposed_parameters = (
            prohibited_parameters
            & set(signature.parameters)
        )

        persisted_audit_actors = {
            actor
            for actor, in (
                db.query(AuditEvent.actor)
                .filter(
                    AuditEvent.id.in_(
                        result.audit_event_ids
                    )
                )
                .all()
            )
        }

        expected_server_actors = {
            SYSTEM_PLATFORM_BOOTSTRAP_ACTOR,
            SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
        }

        server_controlled_actors_only = (
            bool(persisted_audit_actors)
            and persisted_audit_actors
            <= expected_server_actors
        )

        security_checks = {
            "No caller-selected authority inputs": (
                not exposed_parameters
            ),
            "Canonical role key returned": (
                result.role_key
                == PLATFORM_ADMINISTRATOR_ROLE_KEY
            ),
            "Canonical permission key returned": (
                result.permission_key
                == PLATFORM_ADMINISTRATION_PERMISSION_KEY
            ),
            "Initial status is Invited": (
                result.platform_user_status
                == PlatformUserStatus.INVITED.value
            ),
            "Authorization granted": (
                result.authorization_granted is True
            ),
            "Seat not allocated": (
                result.seat_allocated is False
            ),
            "Authentication not completed": (
                result.authentication_completed is False
            ),
            "Server-controlled audit actors only": (
                server_controlled_actors_only
            ),
        }

        for label, passed in security_checks.items():
            print_check(label, passed)

            if not passed:
                errors.append(
                    f"Security contract failed: {label}."
                )

        print()
        print("=" * 42)

        if errors:
            print("OVERALL RESULT........................ FAILED")
            print()

            for error in errors:
                print(f"- {error}")

            return 1

        print("OVERALL RESULT........................ PASSED")
        print()
        print(
            "PlatformBootstrapService atomically creates the "
            "initial Platform Administrator identity, canonical "
            "authorization vocabulary, permission mapping, role "
            "assignment, and immutable audit trail with one "
            "server-owned transaction."
        )

        return 0

    finally:
        bootstrap_module.PLATFORM_ADMINISTRATOR_ROLE_KEY = (
            original_role_key
        )
        bootstrap_module.PLATFORM_ADMINISTRATION_PERMISSION_KEY = (
            original_permission_key
        )
        bootstrap_module.PLATFORM_ADMINISTRATION_RESOURCE = (
            original_resource
        )
        bootstrap_module.PLATFORM_ADMINISTRATION_ACTION = (
            original_action
        )

        db.rollback()

        if organization_ids:
            role_ids = [
                item[0]
                for item in (
                    db.query(PlatformRole.id)
                    .filter(
                        PlatformRole.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            user_ids = [
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

            assignment_ids = [
                item[0]
                for item in (
                    db.query(PlatformRoleAssignment.id)
                    .filter(
                        PlatformRoleAssignment.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            mapping_ids = [
                item[0]
                for item in (
                    db.query(PlatformRolePermission.id)
                    .filter(
                        PlatformRolePermission.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            audit_entity_ids = (
                user_ids
                + role_ids
                + assignment_ids
                + mapping_ids
                + organization_ids
            )

            if audit_entity_ids:
                (
                    db.query(AuditEvent)
                    .filter(
                        AuditEvent.entity_id.in_(
                            audit_entity_ids
                        )
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            (
                db.query(PlatformRoleAssignment)
                .filter(
                    PlatformRoleAssignment.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(PlatformRolePermission)
                .filter(
                    PlatformRolePermission.organization_id.in_(
                        organization_ids
                    )
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
                db.query(PlatformRole)
                .filter(
                    PlatformRole.organization_id.in_(
                        organization_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            if created_permission_ids:
                (
                    db.query(PlatformPermission)
                    .filter(
                        PlatformPermission.id.in_(
                            created_permission_ids
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
