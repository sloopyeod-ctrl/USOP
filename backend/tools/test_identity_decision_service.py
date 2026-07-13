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
from app.intelligence.identity_intelligence_service import (
    IdentityIntelligenceService,
)


IDENTITY_ID = (
    "da6ea20f-f3d0-4596-b7a1-021202da549e"
)

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
            if (
                str(key).lower()
                in FORBIDDEN_FIELDS
            ):
                findings.append(
                    f"{path}.{key}"
                )

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
        "USOP Identity Decision Service Regression"
    )
    print(
        "-----------------------------------------"
    )

    db = SessionLocal()

    try:
        service = IdentityIntelligenceService(
            db
        )

        first = service.get_identity_intelligence(
            IDENTITY_ID
        )
        second = service.get_identity_intelligence(
            IDENTITY_ID
        )

        errors = []

        if first is None or second is None:
            errors.append(
                "Identity intelligence returned no result."
            )
        else:
            decision = first.get("decision")

            if not decision:
                errors.append(
                    "Identity decision was not returned."
                )
            else:
                if not decision.get("available"):
                    errors.append(
                        "Identity decision is unavailable."
                    )

                if decision.get("priority") not in {
                    "Critical",
                    "High",
                    "Moderate",
                    "Medium",
                    "Low",
                    "Unknown",
                }:
                    errors.append(
                        "Decision priority is invalid."
                    )

                confidence = decision.get(
                    "confidence",
                    {},
                )

                confidence_score = confidence.get(
                    "score"
                )

                if not isinstance(
                    confidence_score,
                    int,
                ):
                    errors.append(
                        "Confidence score is not an integer."
                    )
                elif not (
                    0 <= confidence_score <= 100
                ):
                    errors.append(
                        "Confidence score is outside "
                        "the valid range."
                    )

                authorization = decision.get(
                    "authorization",
                    {},
                )

                if (
                    authorization.get(
                        "role_count"
                    )
                    != 3
                ):
                    errors.append(
                        "Decision does not contain all "
                        "three live role assignments."
                    )

                if (
                    authorization.get(
                        "tenant_wide_assignment_count"
                    )
                    != 3
                ):
                    errors.append(
                        "Tenant-wide assignment count "
                        "is incorrect."
                    )

                classifications = (
                    authorization.get(
                        "role_classifications",
                        [],
                    )
                )

                levels = {
                    item.get("role_name"):
                    item.get("risk_level")
                    for item in classifications
                }

                if (
                    levels.get(
                        "Global Administrator"
                    )
                    != "Critical"
                ):
                    errors.append(
                        "Global Administrator was not "
                        "classified as Critical."
                    )

        if (
            json.dumps(
                first,
                sort_keys=True,
                default=str,
            )
            != json.dumps(
                second,
                sort_keys=True,
                default=str,
            )
        ):
            errors.append(
                "Repeated evaluation produced "
                "different decision intelligence."
            )

        forbidden = find_forbidden_fields(
            first
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

        decision = first["decision"]
        authorization = decision[
            "authorization"
        ]

        print(
            "Identity: "
            f"{first['identity']['display_name']}"
        )
        print(
            "Priority: "
            f"{decision['priority']}"
        )
        print(
            "Decision title: "
            f"{decision['summary']['title']}"
        )
        print(
            "Confidence: "
            f"{decision['confidence']['score']}%"
        )
        print(
            "Accounts: "
            f"{authorization['account_count']}"
        )
        print(
            "Groups: "
            f"{authorization['group_count']}"
        )
        print(
            "Roles: "
            f"{authorization['role_count']}"
        )
        print(
            "High-impact roles: "
            f"{authorization['privileged_role_count']}"
        )
        print(
            "Tenant-wide assignments: "
            f"{authorization['tenant_wide_assignment_count']}"
        )
        print(
            "Direct assignments: "
            f"{authorization['direct_assignment_count']}"
        )
        print(
            "Recommended actions: "
            f"{len(decision['recommended_actions'])}"
        )
        print(
            "Estimated risk reduction: "
            f"{decision['estimated_risk_reduction']}"
        )
        print(
            "Next step: "
            f"{decision['next_step']}"
        )

        print()
        print("Role classifications:")

        for classification in (
            authorization[
                "role_classifications"
            ]
        ):
            print("-" * 60)
            print(
                "Role: "
                f"{classification['role_name']}"
            )
            print(
                "Risk: "
                f"{classification['risk_level']}"
            )
            print(
                "Capability: "
                f"{classification['capability']}"
            )
            print(
                "Scope: "
                f"{classification['scope']}"
            )
            print(
                "Assignment: "
                f"{classification['assignment']}"
            )

        print()
        print("Validation: PASSED")
        print(
            "Identity decision intelligence is "
            "deterministic, explainable, evidence-based, "
            "and free of sensitive fields."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
