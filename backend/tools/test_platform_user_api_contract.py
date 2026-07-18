import sys
import uuid
import warnings
from datetime import datetime, timezone
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
from app.models.organization import Organization
from app.models.platform_user import PlatformUser


ACTOR = "USOP Platform User API Contract Regression"


def main() -> int:
    print("USOP Platform User API Contract Regression")
    print("------------------------------------------")

    db = SessionLocal()
    client = TestClient(app)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_ids: list[str] = []
    platform_user_ids: list[str] = []
    errors: list[str] = []

    try:
        primary_organization = Organization(
            name="Platform User API Primary",
            slug=f"platform-user-api-primary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_organization = Organization(
            name="Platform User API Secondary",
            slug=f"platform-user-api-secondary-{suffix}",
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

        organization_ids.extend(
            [
                primary_organization.id,
                secondary_organization.id,
            ]
        )

        primary_user = PlatformUser(
            organization_id=primary_organization.id,
            display_name="Primary Platform Operator",
            email=f"primary-{suffix}@example.invalid",
            status="Invited",
            identity_provider="MicrosoftEntraID",
            external_tenant_id=str(uuid.uuid4()),
            external_subject_id=str(uuid.uuid4()),
            identity_issuer=None,
            created_via_bootstrap=False,
            invited_at=now,
            activated_at=None,
            last_authenticated_at=None,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_user = PlatformUser(
            organization_id=secondary_organization.id,
            display_name="Secondary Platform Operator",
            email=f"secondary-{suffix}@example.invalid",
            status="Invited",
            identity_provider="MicrosoftEntraID",
            external_tenant_id=str(uuid.uuid4()),
            external_subject_id=str(uuid.uuid4()),
            identity_issuer=None,
            created_via_bootstrap=False,
            invited_at=now,
            activated_at=None,
            last_authenticated_at=None,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(primary_user)
        db.add(secondary_user)
        db.commit()

        db.refresh(primary_user)
        db.refresh(secondary_user)

        platform_user_ids.extend(
            [
                primary_user.id,
                secondary_user.id,
            ]
        )

        openapi_response = client.get(
            "/openapi.json"
        )

        list_response = client.get(
            (
                "/api/v1/organizations/"
                f"{primary_organization.id}/platform-users/"
            )
        )

        get_response = client.get(
            (
                "/api/v1/organizations/"
                f"{primary_organization.id}/platform-users/"
                f"{primary_user.id}"
            )
        )

        cross_organization_response = client.get(
            (
                "/api/v1/organizations/"
                f"{primary_organization.id}/platform-users/"
                f"{secondary_user.id}"
            )
        )

        unknown_organization_response = client.get(
            (
                "/api/v1/organizations/"
                f"{uuid.uuid4()}/platform-users/"
            )
        )

        unknown_user_response = client.get(
            (
                "/api/v1/organizations/"
                f"{primary_organization.id}/platform-users/"
                f"{uuid.uuid4()}"
            )
        )

        if openapi_response.status_code != 200:
            errors.append(
                "OpenAPI contract was unavailable."
            )
        else:
            paths = openapi_response.json()["paths"]

            expected_paths = {
                (
                    "/api/v1/organizations/"
                    "{organization_id}/platform-users/"
                ),
                (
                    "/api/v1/organizations/"
                    "{organization_id}/platform-users/"
                    "{platform_user_id}"
                ),
            }

            for path in expected_paths:
                if path not in paths:
                    errors.append(
                        f"OpenAPI is missing {path}."
                    )
                    continue

                if set(paths[path]) != {"get"}:
                    errors.append(
                        f"OpenAPI exposes non-GET methods for {path}."
                    )

        if list_response.status_code != 200:
            errors.append(
                "Platform User list endpoint did not return 200."
            )
        else:
            payload = list_response.json()

            if len(payload) != 1:
                errors.append(
                    "Platform User list endpoint returned an "
                    "unexpected record count."
                )
            elif payload[0]["id"] != primary_user.id:
                errors.append(
                    "Platform User list endpoint returned the "
                    "wrong Organization record."
                )

            prohibited = {
                "password",
                "password_hash",
                "access_token",
                "refresh_token",
                "seat_id",
                "seat_allocated",
                "role_id",
                "permission_id",
                "authorization_granted",
                "actor",
                "created_by",
                "updated_by",
            }

            if payload and prohibited & set(payload[0]):
                errors.append(
                    "Platform User list response exposed "
                    "prohibited fields."
                )

        if get_response.status_code != 200:
            errors.append(
                "Platform User detail endpoint did not return 200."
            )
        elif get_response.json()["id"] != primary_user.id:
            errors.append(
                "Platform User detail endpoint returned the "
                "wrong record."
            )

        if cross_organization_response.status_code != 404:
            errors.append(
                "Cross-Organization Platform User lookup was "
                "not hidden with 404."
            )

        if unknown_organization_response.status_code != 404:
            errors.append(
                "Unknown Organization listing did not return 404."
            )

        if unknown_user_response.status_code != 404:
            errors.append(
                "Unknown Platform User lookup did not return 404."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "OpenAPI available: "
            f"{openapi_response.status_code == 200}"
        )
        print(
            "Read-only methods exposed: True"
        )
        print(
            "Organization-scoped list returned: "
            f"{list_response.status_code == 200}"
        )
        print(
            "Organization-scoped detail returned: "
            f"{get_response.status_code == 200}"
        )
        print(
            "Cross-Organization lookup hidden: "
            f"{cross_organization_response.status_code == 404}"
        )
        print(
            "Unknown Organization rejected: "
            f"{unknown_organization_response.status_code == 404}"
        )
        print(
            "Unknown Platform User hidden: "
            f"{unknown_user_response.status_code == 404}"
        )
        print(
            "Credentials exposed: False"
        )
        print(
            "Tokens exposed: False"
        )
        print(
            "Seat state exposed: False"
        )
        print(
            "Authorization exposed: False"
        )
        print(
            "Audit actors exposed: False"
        )

        print()
        print("Validation: PASSED")
        print(
            "The Platform User API exposes only Organization-scoped, "
            "read-only lifecycle and external identity facts while "
            "hiding cross-Organization records and excluding credentials, "
            "tokens, Seat state, authorization, and audit actors."
        )

        return 0

    finally:
        db.rollback()

        if platform_user_ids:
            (
                db.query(PlatformUser)
                .filter(
                    PlatformUser.id.in_(
                        platform_user_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

        if organization_ids:
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
