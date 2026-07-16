import sys
from pathlib import Path

from sqlalchemy import ForeignKeyConstraint


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


from app.database.base import Base
from app.models.license import License


def main() -> int:
    print("USOP Canonical License Model Regression")
    print("---------------------------------------")

    errors: list[str] = []

    table = License.__table__

    expected_columns = {
        "id",
        "organization_id",
        "license_identifier",
        "status",
        "commercial_edition",
        "commercial_purpose",
        "license_format_version",
        "issued_at",
        "effective_at",
        "expires_at",
        "deployment_identifier",
        "seat_limit",
        "commercial_modules_json",
        "feature_entitlements_json",
        "canonical_payload_json",
        "canonical_payload_hash",
        "signature",
        "signing_key_identifier",
        "supersedes_license_id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "is_active",
    }

    actual_columns = set(table.columns.keys())

    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    if missing_columns:
        errors.append(
            "Missing License columns: "
            + ", ".join(sorted(missing_columns))
        )

    if unexpected_columns:
        errors.append(
            "Unexpected License columns: "
            + ", ".join(sorted(unexpected_columns))
        )

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in table.foreign_keys
    }

    if "organizations.id" not in foreign_keys:
        errors.append(
            "License.organization_id does not reference organizations.id."
        )

    if "licenses.id" not in foreign_keys:
        errors.append(
            "License supersession does not reference licenses.id."
        )

    if not table.c.license_identifier.unique:
        errors.append(
            "License identifier is not unique."
        )

    if table.c.canonical_payload_json.nullable:
        errors.append(
            "Canonical signed payload is nullable."
        )

    if table.c.signature.nullable:
        errors.append(
            "License signature is nullable."
        )

    if table.c.signing_key_identifier.nullable:
        errors.append(
            "Signing key identifier is nullable."
        )

    prohibited_columns = {
        "private_key",
        "signing_private_key",
        "client_secret",
        "provider_credentials",
        "subscription_state",
        "active_seat_count",
        "validation_status",
    }

    present_prohibited = (
        prohibited_columns & actual_columns
    )

    if present_prohibited:
        errors.append(
            "Prohibited License columns detected: "
            + ", ".join(sorted(present_prohibited))
        )

    if "licenses" not in Base.metadata.tables:
        errors.append(
            "License table is not registered with shared metadata."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print(f"Table: {table.name}")
    print(f"Column count: {len(actual_columns)}")
    print("Organization binding: organizations.id")
    print("Historical supersession: licenses.id")
    print("License identifier unique: True")
    print("Canonical payload required: True")
    print("Signature required: True")
    print("Private signing key stored: False")
    print("Subscription State embedded: False")
    print("Active seat accounting embedded: False")

    print()
    print("Validation: PASSED")
    print(
        "The canonical License model preserves organization binding, "
        "immutable signed commercial payload data, historical license "
        "supersession, and architectural separation from runtime "
        "Subscription State."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
