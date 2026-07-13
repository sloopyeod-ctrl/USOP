import json
import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.graph.identity_graph_service import (
    IdentityGraphService,
)
from app.security.authorization import (
    AuthorizationClassificationService,
)


IDENTITY_ID = (
    "da6ea20f-f3d0-4596-b7a1-021202da549e"
)

EXPECTED_LEVELS = {
    "Global Administrator": "Critical",
    "Security Operator": "High",
    "User Administrator": "High",
}

FORBIDDEN_FIELDS = {
    "access_token",
    "refresh_token",
    "client_secret",
    "password",
    "credential",
    "credentials",
    "secret",
    "raw_payload",
}


def find_forbidden_fields(
    value,
    path="root",
):
    findings = []

    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_FIELDS:
                findings.append(f"{path}.{key}")

            findings.extend(
                find_forbidden_fields(
                    child,
                    f"{path}.{key}",
                )
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                find_forbidden_fields(
                    child,
                    f"{path}[{index}]",
                )
            )

    return findings


def main() -> int:
    print(
        "USOP Authorization Classification Regression"
    )
    print(
        "--------------------------------------------"
    )

    db = SessionLocal()

    try:
        graph = IdentityGraphService(
            db
        ).get_identity_graph(
            IDENTITY_ID
        )

        if graph is None:
            print("Validation: FAILED")
            print("- Identity graph returned no result.")
            return 1

        classifier = (
            AuthorizationClassificationService()
        )

        classifications = [
            classifier.classify(role)
            for role in graph["roles"]
        ]

        repeated = [
            classifier.classify(role)
            for role in graph["roles"]
        ]

        errors = []

        if (
            json.dumps(
                classifications,
                sort_keys=True,
            )
            != json.dumps(
                repeated,
                sort_keys=True,
            )
        ):
            errors.append(
                "Repeated classification produced "
                "different results."
            )

        for role, classification in zip(
            graph["roles"],
            classifications,
            strict=True,
        ):
            role_name = role["role_name"]
            expected_level = EXPECTED_LEVELS.get(
                role_name
            )

            if expected_level and (
                classification["risk_level"]
                != expected_level
            ):
                errors.append(
                    f"{role_name} expected "
                    f"{expected_level} but received "
                    f"{classification['risk_level']}."
                )

            if role.get("directory_scope") == "/" and (
                classification[
                    "scope_classification"
                ]
                != "TenantWide"
            ):
                errors.append(
                    f"{role_name} tenant scope was "
                    "not classified correctly."
                )

        unknown_result = classifier.classify(
            {
                "role_name": "Unrecognized Role",
                "role_source_identifier": (
                    "unknown-role"
                ),
                "system_name": "Unknown Provider",
                "privilege_level": None,
                "assignment_type": "Direct",
                "directory_scope": "/",
                "application_scope": None,
            }
        )

        if (
            unknown_result["risk_level"]
            != "Unknown"
        ):
            errors.append(
                "Unknown role evidence was guessed "
                "instead of remaining Unknown."
            )

        explicit_result = classifier.classify(
            {
                "role_name": "Custom Reader",
                "role_source_identifier": (
                    "custom-reader"
                ),
                "system_name": "Custom Provider",
                "privilege_level": "ReadOnly",
                "assignment_type": "Direct",
                "directory_scope": "/",
                "application_scope": None,
            }
        )

        if explicit_result["risk_level"] != "Low":
            errors.append(
                "Explicit canonical ReadOnly metadata "
                "did not override provider policy."
            )

        forbidden = find_forbidden_fields(
            classifications
        )

        if forbidden:
            errors.append(
                "Sensitive fields were exposed: "
                f"{forbidden}"
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Identity: "
            f"{graph['identity']['display_name']}"
        )

        for role, classification in sorted(
            zip(
                graph["roles"],
                classifications,
                strict=True,
            ),
            key=lambda item: item[0]["role_name"],
        ):
            print("-" * 60)
            print(
                f"Role: {role['role_name']}"
            )
            print(
                "Risk level: "
                f"{classification['risk_level']}"
            )
            print(
                "Capability: "
                f"{classification['capability']}"
            )
            print(
                "Scope: "
                f"{classification['scope_classification']}"
            )
            print(
                "Assignment: "
                f"{classification['assignment_classification']}"
            )
            print(
                "Source: "
                f"{classification['classification_source']}"
            )

        print()
        print("Validation: PASSED")
        print(
            "Authorization classifications are "
            "deterministic, evidence-based, "
            "provider-aware, and fail safely."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
