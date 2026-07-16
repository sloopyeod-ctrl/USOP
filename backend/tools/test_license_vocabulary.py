import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.domain.license_status import LicenseStatus


def main() -> int:
    print("USOP Canonical License Vocabulary Regression")
    print("-------------------------------------------")

    expected_license_statuses = {
        "Issued",
        "Superseded",
        "Revoked",
    }

    expected_editions = {
        "Community",
        "Starter",
        "Professional",
        "Enterprise",
    }

    expected_purposes = {
        "Internal",
        "Development",
        "Evaluation",
        "Beta",
        "Production",
        "Partner",
    }

    actual_license_statuses = {
        item.value
        for item in LicenseStatus
    }

    actual_editions = {
        item.value
        for item in CommercialEdition
    }

    actual_purposes = {
        item.value
        for item in CommercialPurpose
    }

    errors: list[str] = []

    if actual_license_statuses != expected_license_statuses:
        errors.append(
            "LicenseStatus values do not match the "
            "canonical vocabulary."
        )

    if actual_editions != expected_editions:
        errors.append(
            "CommercialEdition values do not match the "
            "canonical vocabulary."
        )

    if actual_purposes != expected_purposes:
        errors.append(
            "CommercialPurpose values do not match the "
            "canonical vocabulary."
        )

    if "Expired" in actual_license_statuses:
        errors.append(
            "Expiration was incorrectly persisted as a "
            "License lifecycle status instead of derived "
            "Subscription State."
        )

    if "Invalid" in actual_license_statuses:
        errors.append(
            "Validation result was incorrectly persisted as "
            "License lifecycle state."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print("License statuses:")

    for item in LicenseStatus:
        print(f"- {item.value}")

    print()
    print("Commercial editions:")

    for item in CommercialEdition:
        print(f"- {item.value}")

    print()
    print("Commercial purposes:")

    for item in CommercialPurpose:
        print(f"- {item.value}")

    print()
    print("Validation: PASSED")
    print(
        "License lifecycle, commercial edition, and "
        "commercial purpose are independently represented "
        "through deterministic canonical vocabularies."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
