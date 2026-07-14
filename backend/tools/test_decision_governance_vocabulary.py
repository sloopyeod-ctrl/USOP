import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


from app.domain import (
    AcceptanceType,
    ApprovalStatus,
    DecisionStatus,
    DecisionType,
    VerificationStatus,
)


EXPECTED_DECISION_TYPES = {
    "AcceptRisk",
    "CorrectRisk",
    "Escalate",
    "Defer",
    "FalsePositive",
}

EXPECTED_DECISION_STATUSES = {
    "Draft",
    "Open",
    "PendingApproval",
    "Approved",
    "Rejected",
    "InProgress",
    "Accepted",
    "Deferred",
    "Escalated",
    "PendingVerification",
    "Verified",
    "Closed",
    "ReviewDue",
    "Overdue",
    "Reopened",
}

EXPECTED_ACCEPTANCE_TYPES = {
    "Temporary",
    "Permanent",
}

EXPECTED_APPROVAL_STATUSES = {
    "NotRequired",
    "Pending",
    "Approved",
    "Rejected",
}

EXPECTED_VERIFICATION_STATUSES = {
    "NotRequired",
    "Pending",
    "Verified",
    "Failed",
}


def enum_values(enum_type):
    return {
        item.value
        for item in enum_type
    }


def main() -> int:
    print(
        "USOP Decision Governance Vocabulary Regression"
    )
    print(
        "----------------------------------------------"
    )

    checks = {
        "DecisionType": (
            enum_values(DecisionType),
            EXPECTED_DECISION_TYPES,
        ),
        "DecisionStatus": (
            enum_values(DecisionStatus),
            EXPECTED_DECISION_STATUSES,
        ),
        "AcceptanceType": (
            enum_values(AcceptanceType),
            EXPECTED_ACCEPTANCE_TYPES,
        ),
        "ApprovalStatus": (
            enum_values(ApprovalStatus),
            EXPECTED_APPROVAL_STATUSES,
        ),
        "VerificationStatus": (
            enum_values(VerificationStatus),
            EXPECTED_VERIFICATION_STATUSES,
        ),
    }

    errors = []

    for name, (
        actual,
        expected,
    ) in checks.items():
        missing = expected - actual
        unexpected = actual - expected

        if missing:
            errors.append(
                f"{name} is missing: "
                f"{sorted(missing)}"
            )

        if unexpected:
            errors.append(
                f"{name} has unexpected values: "
                f"{sorted(unexpected)}"
            )

        print(
            f"{name}: "
            f"{', '.join(sorted(actual))}"
        )

    if (
        ApprovalStatus.NOT_REQUIRED.value
        != "NotRequired"
    ):
        errors.append(
            "ApprovalStatus.NotRequired is not "
            "represented explicitly."
        )

    if (
        VerificationStatus.NOT_REQUIRED.value
        != "NotRequired"
    ):
        errors.append(
            "VerificationStatus.NotRequired is not "
            "represented explicitly."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print()
    print("Validation: PASSED")
    print(
        "Decision governance vocabulary is canonical, "
        "policy-neutral, and ready for lifecycle rules."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
