import sys
import uuid
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

warnings.filterwarnings(
    "ignore",
    message=".*starlette.testclient.*deprecated.*",
)

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
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


ACTOR = "USOP Platform Bootstrap API Contract Regression"

EXPECTED_PATH = (
    "/api/v1/organizations/"
    "{organization_id}/platform-bootstrap/"
)


def build_organization(
    *,
    suffix: str,
    label: str,
) -> Organization:
    return Organization(
        name=f"Platform Bootstrap API {label}",
        slug=(
            f"platform-bootstrap-api-"
            f"{label.lower()}-{suffix}"
        ),
        status="Active",
        organization_type="Customer",
        primary_domain=None,
        time_zone="UTC",
        description=None,
        external_reference=None,
        deployment_identifier=(
            f"platform-bootstrap-api-{label.lower()}-{suffix}"
        ),
        settings_json=None,
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def build_license(
    *,
    organization: Organization,
    suffix: str,
    now: datetime,
) -> License:
    canonical_payload = {
        "organization_id": organization.id,
        "license_identifier": (
            f"platform-bootstrap-api-license-{suffix}"
        ),
        "commercial_edition": "Professional",
        "commercial_purpose": "Development",
        "license_format_version": "1.0",
        "issued_at": now.isoformat(),
    }

    return License(
        organization_id=organization.id,
        license_identifier=(
            f"platform-bootstrap-api-license-{suffix}"
        ),
        status="Issued",
        commercial_edition="Professional",
        commercial_purpose="Development",
        license_format_version="1.0",
        issued_at=now,
        effective_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(days=30),
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
        canonical_payload_json=canonical_payload,
        canonical_payload_hash="a" * 64,
        signature="platform-bootstrap-api-signature",
        signing_key_identifier=(
            "platform-bootstrap-api-regression-key"
        ),
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def print_check(
    label: str,
    passed: bool,
) -> None:
    dots = "." * max(1, 44 - len(label))
    print(
        f"{label}{dots}"
        f"{'PASS' if passed else 'FAIL'}"
    )


def main() -> int:
    print("USOP Platform Bootstrap API Contract Regression")
    print("===============================================")

    db = SessionLocal()
    client = TestClient(app)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_ids: list[str] = []
    errors: list[str] = []

    try:
        happy_organization = build_organization(
            suffix=suffix,
            label="Happy",
        )

        unlicensed_organization = build_organization(
            suffix=suffix,
            label="Unlicensed",
        )

        db.add(happy_organization)
        db.add(unlicensed_organization)
        db.flush()

        organization_ids.extend(
            [
                happy_organization.id,
                unlicensed_organization.id,
            ]
        )

        eligible_license = build_license(
            organization=happy_organization,
            suffix=suffix,
            now=now,
        )

        db.add(eligible_license)
        db.commit()

        bootstrap_payload = {
            "display_name": (
                "Initial Platform Administrator"
            ),
            "email": (
                f"administrator-{suffix}@example.com"
            ),
            "identity_provider": "MicrosoftEntraID",
            "external_tenant_id": str(uuid.uuid4()),
            "external_subject_id": str(uuid.uuid4()),
            "identity_issuer": (
                "https://login.microsoftonline.us/"
                f"{uuid.uuid4()}/v2.0"
            ),
        }

        openapi_response = client.get(
            "/openapi.json"
        )

        happy_response = client.post(
            (
                "/api/v1/organizations/"
                f"{happy_organization.id}/"
                "platform-bootstrap/"
            ),
            json=bootstrap_payload,
        )

        second_response = client.post(
            (
                "/api/v1/organizations/"
                f"{happy_organization.id}/"
                "platform-bootstrap/"
            ),
            json={
                **bootstrap_payload,
                "email": (
                    f"second-{suffix}@example.com"
                ),
                "external_subject_id": str(uuid.uuid4()),
            },
        )

        unknown_response = client.post(
            (
                "/api/v1/organizations/"
                f"{uuid.uuid4()}/"
                "platform-bootstrap/"
            ),
            json={
                **bootstrap_payload,
                "external_subject_id": str(uuid.uuid4()),
            },
        )

        unlicensed_response = client.post(
            (
                "/api/v1/organizations/"
                f"{unlicensed_organization.id}/"
                "platform-bootstrap/"
            ),
            json={
                **bootstrap_payload,
                "email": (
                    f"unlicensed-{suffix}@example.com"
                ),
                "external_tenant_id": str(uuid.uuid4()),
                "external_subject_id": str(uuid.uuid4()),
            },
        )

        malformed_response = client.post(
            (
                "/api/v1/organizations/"
                f"{unlicensed_organization.id}/"
                "platform-bootstrap/"
            ),
            json={
                "display_name": "",
                "email": "not-an-email",
            },
        )

        openapi_available = (
            openapi_response.status_code == 200
        )

        post_only = False

        if openapi_available:
            paths = openapi_response.json()["paths"]

            if EXPECTED_PATH in paths:
                post_only = (
                    set(paths[EXPECTED_PATH]) == {"post"}
                )

        happy_created = (
            happy_response.status_code == 201
        )

        response_contract_safe = False
        result_payload = {}

        if happy_created:
            result_payload = happy_response.json()

            required_fields = {
                "organization_id",
                "license_id",
                "platform_user_id",
                "platform_role_id",
                "platform_permission_id",
                "role_permission_mapping_id",
                "role_assignment_id",
                "audit_event_ids",
                "platform_user_status",
                "role_key",
                "permission_key",
                "authorization_granted",
                "seat_allocated",
                "authentication_completed",
            }

            prohibited_fields = {
                "password",
                "password_hash",
                "access_token",
                "refresh_token",
                "client_secret",
                "credential",
                "token",
                "actor",
                "created_by",
                "updated_by",
            }

            response_contract_safe = (
                required_fields
                <= set(result_payload)
                and not (
                    prohibited_fields
                    & set(result_payload)
                )
            )

        persisted_graph_complete = False
        audit_trail_complete = False

        if happy_created:
            platform_user_count = (
                db.query(PlatformUser)
                .filter(
                    PlatformUser.organization_id
                    == happy_organization.id
                )
                .count()
            )

            platform_role_count = (
                db.query(PlatformRole)
                .filter(
                    PlatformRole.organization_id
                    == happy_organization.id
                )
                .count()
            )

            role_assignment_count = (
                db.query(PlatformRoleAssignment)
                .filter(
                    PlatformRoleAssignment.organization_id
                    == happy_organization.id
                )
                .count()
            )

            permission_mapping_count = (
                db.query(PlatformRolePermission)
                .filter(
                    PlatformRolePermission.organization_id
                    == happy_organization.id
                )
                .count()
            )

            permission_count = (
                db.query(PlatformPermission)
                .filter(
                    PlatformPermission.permission_key
                    == "platform-administration.manage"
                )
                .count()
            )

            persisted_graph_complete = (
                platform_user_count == 1
                and platform_role_count == 1
                and role_assignment_count == 1
                and permission_mapping_count == 1
                and permission_count == 1
            )

            returned_audit_ids = set(
                result_payload.get(
                    "audit_event_ids",
                    [],
                )
            )

            persisted_audit_ids = {
                item[0]
                for item in (
                    db.query(AuditEvent.id)
                    .filter(
                        AuditEvent.id.in_(
                            returned_audit_ids
                        )
                    )
                    .all()
                )
            }

            audit_trail_complete = (
                bool(returned_audit_ids)
                and returned_audit_ids
                == persisted_audit_ids
            )

        checks = {
            "OpenAPI available": openapi_available,
            "Only POST exposed": post_only,
            "Happy path returned 201": happy_created,
            "Response contract is safe": (
                response_contract_safe
            ),
            "Bootstrap graph persisted": (
                persisted_graph_complete
            ),
            "Audit trail persisted": audit_trail_complete,
            "Second bootstrap returned 409": (
                second_response.status_code == 409
            ),
            "Unknown Organization returned 404": (
                unknown_response.status_code == 404
            ),
            "Missing License returned 409": (
                unlicensed_response.status_code == 409
            ),
            "Malformed request returned 422": (
                malformed_response.status_code == 422
            ),
        }

        for label, passed in checks.items():
            print_check(label, passed)

            if not passed:
                errors.append(label)

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            print()
            print(
                "Happy response: "
                f"{happy_response.status_code} "
                f"{happy_response.text}"
            )
            print(
                "Second response: "
                f"{second_response.status_code} "
                f"{second_response.text}"
            )
            print(
                "Unknown response: "
                f"{unknown_response.status_code} "
                f"{unknown_response.text}"
            )
            print(
                "Unlicensed response: "
                f"{unlicensed_response.status_code} "
                f"{unlicensed_response.text}"
            )

            return 1

        print()
        print("Validation: PASSED")
        print(
            "The Platform Bootstrap API exposes one "
            "Organization-scoped POST operation that delegates "
            "the atomic identity, authorization, License, and "
            "audit lifecycle to PlatformBootstrapService."
        )

        return 0

    finally:
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

            license_ids = [
                item[0]
                for item in (
                    db.query(License.id)
                    .filter(
                        License.organization_id.in_(
                            organization_ids
                        )
                    )
                    .all()
                )
            ]

            entity_ids = (
                organization_ids
                + role_ids
                + user_ids
                + license_ids
            )

            (
                db.query(AuditEvent)
                .filter(
                    (
                        AuditEvent.entity_id.in_(
                            entity_ids
                        )
                    )
                    | (
                        AuditEvent.metadata_json[
                            "organization_id"
                        ].as_string().in_(
                            organization_ids
                        )
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
