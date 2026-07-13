import json
import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.graph.identity_graph_service import (
    IdentityGraphService,
)


IDENTITY_ID = (
    "da6ea20f-f3d0-4596-b7a1-021202da549e"
)

REQUIRED_ROLE_FIELDS = {
    "role_id",
    "role_name",
    "subject_type",
    "subject_id",
    "account_id",
    "username",
    "system_name",
    "privilege_level",
    "assignment_type",
    "directory_scope",
    "application_scope",
}

FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "refresh_token",
    "client_secret",
    "password",
    "credential",
    "credentials",
    "raw_payload",
    "secret",
}


def find_forbidden_fields(
    value,
    path="root",
):
    findings = []

    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = str(key).lower()

            if normalized_key in FORBIDDEN_FIELD_NAMES:
                findings.append(
                    f"{path}.{key}"
                )

            findings.extend(
                find_forbidden_fields(
                    item,
                    f"{path}.{key}",
                )
            )

    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(
                find_forbidden_fields(
                    item,
                    f"{path}[{index}]",
                )
            )

    return findings


def normalized_payload(graph):
    return json.dumps(
        graph,
        sort_keys=True,
        default=str,
    )


def main() -> int:
    print(
        "USOP Authorization Evidence Regression"
    )
    print(
        "--------------------------------------"
    )

    db = SessionLocal()

    try:
        service = IdentityGraphService(db)

        first_graph = service.get_identity_graph(
            IDENTITY_ID
        )
        second_graph = service.get_identity_graph(
            IDENTITY_ID
        )

        errors = []

        if first_graph is None:
            errors.append(
                "Identity graph returned no result."
            )

        if second_graph is None:
            errors.append(
                "Repeated identity graph evaluation "
                "returned no result."
            )

        if errors:
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        roles = first_graph.get(
            "roles",
            [],
        )

        if not roles:
            errors.append(
                "No assigned roles were returned."
            )

        for index, role in enumerate(roles):
            missing_fields = (
                REQUIRED_ROLE_FIELDS
                - set(role.keys())
            )

            if missing_fields:
                errors.append(
                    "Role "
                    f"{index + 1} is missing fields: "
                    f"{sorted(missing_fields)}"
                )

            if not role.get("assignment_type"):
                errors.append(
                    "Role "
                    f"{index + 1} has no "
                    "assignment type."
                )

        forbidden_fields = find_forbidden_fields(
            first_graph
        )

        if forbidden_fields:
            errors.append(
                "Sensitive fields were exposed: "
                f"{forbidden_fields}"
            )

        if (
            normalized_payload(first_graph)
            != normalized_payload(second_graph)
        ):
            errors.append(
                "Repeated evaluation produced "
                "different authorization evidence."
            )

        tenant_wide_roles = [
            role
            for role in roles
            if role.get("directory_scope") == "/"
        ]

        direct_assignments = [
            role
            for role in roles
            if role.get("assignment_type")
            == "Direct"
        ]

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Identity: "
            f"{first_graph['identity']['display_name']}"
        )
        print(
            "Accounts: "
            f"{len(first_graph['accounts'])}"
        )
        print(
            "Groups: "
            f"{len(first_graph['groups'])}"
        )
        print(
            "Roles: "
            f"{len(roles)}"
        )
        print(
            "Direct assignments: "
            f"{len(direct_assignments)}"
        )
        print(
            "Tenant-wide assignments: "
            f"{len(tenant_wide_roles)}"
        )

        print()
        print("Authorization evidence:")

        for role in sorted(
            roles,
            key=lambda item: (
                item.get("role_name") or ""
            ),
        ):
            print("-" * 60)
            print(
                "Role: "
                f"{role.get('role_name')}"
            )
            print(
                "Privilege: "
                f"{role.get('privilege_level')}"
            )
            print(
                "Assignment type: "
                f"{role.get('assignment_type')}"
            )
            print(
                "Directory scope: "
                f"{role.get('directory_scope')}"
            )
            print(
                "Application scope: "
                f"{role.get('application_scope')}"
            )

        print()
        print("Validation: PASSED")
        print(
            "Canonical role-assignment evidence is "
            "available for deterministic decision "
            "intelligence without exposing secrets."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
