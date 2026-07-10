import sys
from pathlib import Path

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

from app.domain.subject_type import SubjectType
from app.schemas.role_assignment import RoleAssignmentCreate


def main() -> int:
    print("USOP Canonical Subject Type Test")
    print("--------------------------------")

    expected_values = {
        "Account",
        "ServicePrincipal",
        "Device",
        "Group",
        "Workload",
        "ExternalPrincipal",
    }

    actual_values = {
        subject_type.value
        for subject_type in SubjectType
    }

    if actual_values != expected_values:
        print("Validation: FAILED")
        print(
            "Canonical subject type values do not match "
            "the expected domain vocabulary."
        )
        return 1

    account_assignment = RoleAssignmentCreate(
        role_id="test-role-id",
        subject_id="test-account-id",
    )

    if (
        account_assignment.subject_type
        != SubjectType.ACCOUNT
    ):
        print("Validation: FAILED")
        print(
            "Role assignments did not default to the "
            "Account subject type."
        )
        return 1

    group_assignment = RoleAssignmentCreate(
        role_id="test-role-id",
        subject_type=SubjectType.GROUP,
        subject_id="test-group-id",
    )

    if (
        group_assignment.subject_type
        != SubjectType.GROUP
    ):
        print("Validation: FAILED")
        print(
            "Role assignments did not accept the "
            "Group subject type."
        )
        return 1

    try:
        RoleAssignmentCreate(
            role_id="test-role-id",
            subject_type="InvalidSubjectType",
            subject_id="test-subject-id",
        )
    except ValidationError:
        invalid_value_rejected = True
    else:
        invalid_value_rejected = False

    if not invalid_value_rejected:
        print("Validation: FAILED")
        print(
            "The schema accepted an invalid subject type."
        )
        return 1

    print("Canonical subject types:")

    for subject_type in SubjectType:
        print(f"- {subject_type.value}")

    print()
    print("Validation: PASSED")
    print(
        "Role assignments now use the shared canonical "
        "subject-type vocabulary."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())