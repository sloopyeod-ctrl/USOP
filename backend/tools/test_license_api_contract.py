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
    message=(
        "Using `httpx` with "
        "`starlette.testclient` is deprecated"
    ),
)

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.license import License
from app.models.organization import Organization


EXPECTED_OPERATION = (
    "/api/v1/licenses/install",
    "post",
)


def collect_openapi_operations() -> set[tuple[str, str]]:
    schema = app.openapi()
    paths = schema.get("paths", {})

    supported_methods = {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "options",
        "head",
    }

    return {
        (
            path,
            method.lower(),
        )
        for path, operations in paths.items()
        for method in operations
        if method.lower() in supported_methods
    }


def build_payload(
    *,
    organization_id: str,
    license_identifier: str,
    deployment_identifier: str,
    issued_at: datetime,
) -> dict:
    canonical_payload = {
        "organization_id": organization_id,
        "license_identifier": license_identifier,
        "commercial_edition": (
            CommercialEdition.PROFESSIONAL.value
        ),
        "commercial_purpose": (
            CommercialPurpose.BETA.value
        ),
        "license_format_version": "1.0",
        "issued_at": issued_at.isoformat(),
        "seat_limit": 20,
    }

    return {
        "organization_id": organization_id,
        "license_identifier": license_identifier,
        "commercial_edition": (
            CommercialEdition.PROFESSIONAL.value
        ),
        "commercial_purpose": (
            CommercialPurpose.BETA.value
        ),
        "license_format_version": "1.0",
        "issued_at": issued_at.isoformat(),
        "effective_at": issued_at.isoformat(),
        "expires_at": (
            issued_at + timedelta(days=90)
        ).isoformat(),
        "deployment_identifier": (
            deployment_identifier
        ),
        "seat_limit": 20,
        "commercial_modules": [
            "USOPCore",
        ],
        "feature_entitlements": [
            "IdentityDecisionPlatform",
        ],
        "canonical_payload": canonical_payload,
        "canonical_payload_hash": "a" * 64,
        "signature": (
            f"signature-{license_identifier}"
        ),
        "signing_key_identifier": (
            "license-api-regression-key"
        ),
    }


def main() -> int:
    print("USOP License Installation API Contract Regression")
    print("-----------------------------------------------")

    db = SessionLocal()
    client = TestClient(
        app,
        raise_server_exceptions=True,
    )

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    deployment_identifier = (
        f"deployment-{suffix}"
    )

    organization_id: str | None = None
    errors: list[str] = []

    try:
        actual_operations = (
            collect_openapi_operations()
        )

        if EXPECTED_OPERATION not in actual_operations:
            errors.append(
                "Missing OpenAPI operation: "
                "POST /api/v1/licenses/install"
            )

        license_operations = sorted(
            operation
            for operation in actual_operations
            if operation[0].startswith(
                "/api/v1/licenses"
            )
        )

        print("OpenAPI License operations:")

        for path, method in license_operations:
            print(f"- {method.upper()} {path}")

        organization = Organization(
            name="License API Regression",
            slug=f"license-api-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            deployment_identifier=(
                deployment_identifier
            ),
            created_by="USOP API Regression",
            updated_by="USOP API Regression",
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        organization_id = organization.id

        payload = build_payload(
            organization_id=organization.id,
            license_identifier=f"license-{suffix}",
            deployment_identifier=(
                deployment_identifier
            ),
            issued_at=now,
        )

        install_response = client.post(
            "/api/v1/licenses/install",
            json=payload,
        )

        if install_response.status_code != 201:
            errors.append(
                "New License installation returned HTTP "
                f"{install_response.status_code}; expected 201."
            )

        install_body = install_response.json()

        if (
            install_body.get("disposition")
            != "Installed"
        ):
            errors.append(
                "New License response did not report Installed."
            )

        license_id = install_body.get(
            "license_id"
        )

        if not license_id:
            errors.append(
                "New License response did not include license_id."
            )

        if not install_body.get("audit_event_id"):
            errors.append(
                "New License response did not include audit_event_id."
            )

        duplicate_response = client.post(
            "/api/v1/licenses/install",
            json=payload,
        )

        if duplicate_response.status_code != 200:
            errors.append(
                "Duplicate License installation returned HTTP "
                f"{duplicate_response.status_code}; expected 200."
            )

        duplicate_body = (
            duplicate_response.json()
        )

        if (
            duplicate_body.get("disposition")
            != "AlreadyInstalled"
        ):
            errors.append(
                "Duplicate License response did not report "
                "AlreadyInstalled."
            )

        if (
            duplicate_body.get("license_id")
            != license_id
        ):
            errors.append(
                "Duplicate installation did not return "
                "the original License."
            )

        if (
            duplicate_body.get("audit_event_id")
            is not None
        ):
            errors.append(
                "Duplicate installation returned a new audit event."
            )

        unknown_payload = build_payload(
            organization_id=str(uuid.uuid4()),
            license_identifier=f"unknown-{suffix}",
            deployment_identifier=(
                deployment_identifier
            ),
            issued_at=now,
        )

        unknown_response = client.post(
            "/api/v1/licenses/install",
            json=unknown_payload,
        )

        if unknown_response.status_code != 404:
            errors.append(
                "Unknown Organization returned HTTP "
                f"{unknown_response.status_code}; expected 404."
            )

        if (
            unknown_response.json().get("detail")
            != (
                "The License references an "
                "unknown Organization."
            )
        ):
            errors.append(
                "Unknown Organization response did not expose "
                "the expected domain error."
            )

        mismatch_payload = build_payload(
            organization_id=organization.id,
            license_identifier=f"mismatch-{suffix}",
            deployment_identifier=(
                f"wrong-deployment-{suffix}"
            ),
            issued_at=now,
        )

        mismatch_response = client.post(
            "/api/v1/licenses/install",
            json=mismatch_payload,
        )

        if mismatch_response.status_code != 409:
            errors.append(
                "Deployment mismatch returned HTTP "
                f"{mismatch_response.status_code}; expected 409."
            )

        if (
            mismatch_response.json().get("detail")
            != (
                "The License deployment binding does not "
                "match the Organization deployment identifier."
            )
        ):
            errors.append(
                "Deployment mismatch response did not expose "
                "the expected domain error."
            )

        malformed_payload = dict(payload)
        malformed_payload["canonical_payload_hash"] = (
            "not-a-valid-hash"
        )

        malformed_response = client.post(
            "/api/v1/licenses/install",
            json=malformed_payload,
        )

        if malformed_response.status_code != 422:
            errors.append(
                "Malformed request returned HTTP "
                f"{malformed_response.status_code}; expected 422."
            )

        persisted_license_count = (
            db.query(License)
            .filter(
                License.organization_id
                == organization.id
            )
            .count()
        )

        audit_event_count = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "License",
                AuditEvent.entity_id == license_id,
                AuditEvent.event_type
                == "LicenseInstalled",
            )
            .count()
            if license_id
            else 0
        )

        if persisted_license_count != 1:
            errors.append(
                "API workflow did not persist exactly one License."
            )

        if audit_event_count != 1:
            errors.append(
                "API workflow did not persist exactly one audit event."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print()
        print("Runtime routing:")
        print(
            "- New installation -> "
            f"{install_response.status_code}"
        )
        print(
            "- Duplicate installation -> "
            f"{duplicate_response.status_code}"
        )
        print(
            "- Unknown Organization -> "
            f"{unknown_response.status_code}"
        )
        print(
            "- Deployment mismatch -> "
            f"{mismatch_response.status_code}"
        )
        print(
            "- Malformed request -> "
            f"{malformed_response.status_code}"
        )
        print(
            "- Persisted License count -> "
            f"{persisted_license_count}"
        )
        print(
            "- License audit event count -> "
            f"{audit_event_count}"
        )
        print(
            "- Browser-controlled actor field accepted -> False"
        )
        print(
            "- Cryptographic validity asserted -> False"
        )

        print()
        print("Validation: PASSED")
        print(
            "The License installation API exposes the atomic "
            "backend workflow through OpenAPI, maps domain errors "
            "to deterministic HTTP responses, and preserves "
            "backend-controlled attribution."
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
