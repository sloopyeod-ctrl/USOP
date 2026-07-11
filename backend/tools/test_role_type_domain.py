import sys
from pathlib import Path

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

from app.domain.role_type import RoleType
from app.schemas.role import RoleCreate


def main() -> int:
    print("USOP Canonical Role Type Test")
    print("-----------------------------")

    expected_values = {
        "Access",
        "Directory",
        "Cloud",
        "Infrastructure",
        "Application",
        "Platform",
        "Data",
        "Custom",
    }

    actual_values = {
        role_type.value
        for role_type in RoleType
    }

    if actual_values != expected_values:
        print("Validation: FAILED")
        print(
            "Canonical role type values do not match "
            "the expected domain vocabulary."
        )
        return 1

    default_role = RoleCreate(
        name="Default Test Role",
        system_name="Test System",
    )

    if default_role.role_type != RoleType.ACCESS:
        print("Validation: FAILED")
        print(
            "Roles did not preserve the existing Access "
            "role-type default."
        )
        return 1

    directory_role = RoleCreate(
        name="Directory Test Role",
        role_type=RoleType.DIRECTORY,
        system_name="Microsoft Entra ID",
    )

    if directory_role.role_type != RoleType.DIRECTORY:
        print("Validation: FAILED")
        print(
            "Roles did not accept the Directory role type."
        )
        return 1

    serialized_role = directory_role.model_dump(
        mode="json"
    )

    if serialized_role["role_type"] != "Directory":
        print("Validation: FAILED")
        print(
            "The Directory role type did not serialize "
            "as its canonical string value."
        )
        return 1

    try:
        RoleCreate(
            name="Invalid Test Role",
            role_type="InvalidRoleType",
            system_name="Test System",
        )
    except ValidationError:
        invalid_value_rejected = True
    else:
        invalid_value_rejected = False

    if not invalid_value_rejected:
        print("Validation: FAILED")
        print(
            "The role schema accepted an invalid role type."
        )
        return 1

    print("Canonical role types:")

    for role_type in RoleType:
        print(f"- {role_type.value}")

    print()
    print("Validation: PASSED")
    print(
        "Roles now use the shared canonical "
        "role-type vocabulary."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())