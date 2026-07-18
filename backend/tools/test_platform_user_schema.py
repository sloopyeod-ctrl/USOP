import sys
from datetime import datetime, timezone
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.platform_user import PlatformUserRead


EXPECTED_FIELDS = {
    "id",
    "organization_id",
    "display_name",
    "email",
    "status",
    "identity_provider",
    "external_tenant_id",
    "external_subject_id",
    "identity_issuer",
    "created_via_bootstrap",
    "invited_at",
    "activated_at",
    "last_authenticated_at",
    "created_at",
    "updated_at",
    "is_active",
}

PROHIBITED_FIELDS = {
    "password",
    "password_hash",
    "access_token",
    "refresh_token",
    "license_id",
    "seat_id",
    "seat_allocated",
    "role_id",
    "permission_id",
    "authorization_granted",
    "actor",
    "created_by",
    "updated_by",
}


class PlatformUserSource:
    def __init__(self):
        now = datetime.now(timezone.utc)

        self.id = "platform-user-id"
        self.organization_id = "organization-id"
        self.display_name = "Platform Administrator"
        self.email = "admin@example.invalid"
        self.status = "Invited"
        self.identity_provider = "MicrosoftEntraID"
        self.external_tenant_id = "external-tenant-id"
        self.external_subject_id = "external-subject-id"
        self.identity_issuer = (
            "https://login.microsoftonline.com/"
            "external-tenant-id/v2.0"
        )
        self.created_via_bootstrap = True
        self.invited_at = now
        self.activated_at = None
        self.last_authenticated_at = None
        self.created_at = now
        self.updated_at = now
        self.is_active = True

        self.password = "must-not-serialize"
        self.access_token = "must-not-serialize"
        self.seat_allocated = True
        self.authorization_granted = True
        self.created_by = "must-not-serialize"


def main() -> int:
    print("USOP Platform User Schema Regression")
    print("------------------------------------")

    errors: list[str] = []

    actual_fields = set(
        PlatformUserRead.model_fields
    )

    missing_fields = (
        EXPECTED_FIELDS - actual_fields
    )

    unexpected_fields = (
        actual_fields - EXPECTED_FIELDS
    )

    prohibited_fields = (
        actual_fields & PROHIBITED_FIELDS
    )

    if missing_fields:
        errors.append(
            "Missing PlatformUserRead fields: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if unexpected_fields:
        errors.append(
            "Unexpected PlatformUserRead fields: "
            + ", ".join(
                sorted(unexpected_fields)
            )
        )

    if prohibited_fields:
        errors.append(
            "PlatformUserRead exposes prohibited fields: "
            + ", ".join(
                sorted(prohibited_fields)
            )
        )

    source = PlatformUserSource()

    schema = PlatformUserRead.model_validate(
        source
    )

    payload = schema.model_dump()

    if set(payload) != EXPECTED_FIELDS:
        errors.append(
            "Serialized PlatformUserRead fields do not "
            "match the approved contract."
        )

    serialized_prohibited_fields = (
        set(payload) & PROHIBITED_FIELDS
    )

    if serialized_prohibited_fields:
        errors.append(
            "Serialized PlatformUserRead exposes prohibited fields: "
            + ", ".join(
                sorted(serialized_prohibited_fields)
            )
        )

    extra_rejected = False

    try:
        PlatformUserRead.model_validate(
            {
                **payload,
                "password": "must-be-rejected",
            }
        )
    except Exception:
        extra_rejected = True

    if not extra_rejected:
        errors.append(
            "PlatformUserRead accepted an unexpected extra field."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print(
        "Approved field count: "
        f"{len(actual_fields)}"
    )
    print(
        "Expected fields present: "
        f"{actual_fields == EXPECTED_FIELDS}"
    )
    print(
        "ORM attribute validation: "
        f"{schema.id == source.id}"
    )
    print(
        "Credentials exposed: "
        f"{bool(set(payload) & {'password', 'password_hash'})}"
    )
    print(
        "Tokens exposed: "
        f"{bool(set(payload) & {'access_token', 'refresh_token'})}"
    )
    print(
        "Seat state exposed: "
        f"{'seat_allocated' in payload}"
    )
    print(
        "Authorization exposed: "
        f"{'authorization_granted' in payload}"
    )
    print(
        "Audit actors exposed: "
        f"{bool(set(payload) & {'actor', 'created_by', 'updated_by'})}"
    )
    print(
        "Unexpected input rejected: "
        f"{extra_rejected}"
    )

    print()
    print("Validation: PASSED")
    print(
        "PlatformUserRead exposes only approved Organization, "
        "identity-binding, lifecycle, and provenance facts while "
        "excluding credentials, tokens, commercial Seat state, "
        "authorization, and audit actors."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
