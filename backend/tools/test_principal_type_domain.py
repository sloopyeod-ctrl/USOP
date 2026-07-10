import sys
from pathlib import Path

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

from app.domain.principal_type import PrincipalType
from app.schemas.role_assignment import RoleAssignmentCreate


def main() -> int:
    print("USOP Canonical Principal Type Test")
    print("----------------------------------")

    expected_values = {
        "Account",
        "ServicePrincipal",
        "Device",
        "Group",
        "Workload",
        "ExternalPrincipal",
    }

    actual_values = {
        principal_type.value
        for principal_type in PrincipalType
    }

    if actual_values != expected_values:
        print("Validation: FAILED")
        print(
            "Canonical principal type values do not match "
            "the expected domain vocabulary."
        )
        return 1

    account_assignment = RoleAssignmentCreate(
        role_id="test-role-id",
        subject_id="test-account-id",
    )

    if (
        account_assignment.subject_type
        != PrincipalType.ACCOUNT
    ):
        print("Validation: FAILED")
        print(
            "Role assignments did not default to the "
            "Account principal type."
        )
        return 1

    group_assignment = RoleAssignmentCreate(
        role_id="test-role-id",
        subject_type=PrincipalType.GROUP,
        subject_id="test-group-id",
    )

    if (
        group_assignment.subject_type
        != PrincipalType.GROUP
    ):
        print("Validation: FAILED")
        print(
            "Role assignments did not accept the "
            "Group principal type."
        )
        return 1

    try:
        RoleAssignmentCreate(
            role_id="test-role-id",
            subject_type="InvalidPrincipalType",
            subject_id="test-principal-id",
        )
    except ValidationError:
        invalid_value_rejected = True
    else:
        invalid_value_rejected = False

    if not invalid_value_rejected:
        print("Validation: FAILED")
        print(
            "The schema accepted an invalid principal type."
        )
        return 1

    print("Canonical principal types:")

    for principal_type in PrincipalType:
        print(f"- {principal_type.value}")

    print()
    print("Validation: PASSED")
    print(
        "Role assignments now use the shared canonical "
        "principal-type vocabulary."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())