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

EXPECTED_ROLES = {
    "Global Administrator",
    "Security Operator",
    "User Administrator",
}


def main() -> int:
    print(
        "USOP Authorization Recommendation Regression"
    )
    print(
        "--------------------------------------------"
    )

    db = SessionLocal()

    try:
        service = IdentityIntelligenceService(db)

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
            recommendations = first.get(
                "recommendations",
                [],
            )

            authorization_recommendations = [
                recommendation
                for recommendation in recommendations
                if recommendation.get(
                    "recommendation_type"
                )
                == "Authorization"
                and recommendation.get(
                    "evidence_type"
                )
                == "CanonicalRoleClassification"
            ]

            represented_roles = {
                recommendation.get("role_name")
                for recommendation
                in authorization_recommendations
            }

            missing_roles = (
                EXPECTED_ROLES - represented_roles
            )

            if missing_roles:
                errors.append(
                    "Missing authorization recommendations "
                    f"for: {sorted(missing_roles)}"
                )

            global_admin = next(
                (
                    recommendation
                    for recommendation
                    in authorization_recommendations
                    if recommendation.get("role_name")
                    == "Global Administrator"
                ),
                None,
            )

            if global_admin is None:
                errors.append(
                    "Global Administrator recommendation "
                    "was not generated."
                )
            elif (
                global_admin.get("severity")
                != "Critical"
            ):
                errors.append(
                    "Global Administrator recommendation "
                    "is not Critical."
                )

            decision_actions = first.get(
                "decision",
                {},
            ).get(
                "recommended_actions",
                [],
            )

            if (
                decision_actions
                != recommendations
            ):
                errors.append(
                    "Decision actions do not match the "
                    "top-level recommendations."
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
                "different recommendations."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        recommendations = first["recommendations"]

        print(
            "Identity: "
            f"{first['identity']['display_name']}"
        )
        print(
            "Total recommendations: "
            f"{len(recommendations)}"
        )

        for recommendation in recommendations:
            print("-" * 60)
            print(
                "Title: "
                f"{recommendation['title']}"
            )
            print(
                "Severity: "
                f"{recommendation['severity']}"
            )
            print(
                "Type: "
                f"{recommendation.get('recommendation_type')}"
            )
            print(
                "Evidence: "
                f"{recommendation.get('evidence_type')}"
            )
            print(
                "Description: "
                f"{recommendation['description']}"
            )
            print(
                "Risk reduction: "
                f"{recommendation['risk_reduction']}"
            )
            print(
                "Effort: "
                f"{recommendation['estimated_effort']}"
            )

        print()
        print(
            "Decision next step: "
            f"{first['decision']['next_step']}"
        )
        print(
            "Estimated risk reduction: "
            f"{first['decision']['estimated_risk_reduction']}"
        )

        print()
        print("Validation: PASSED")
        print(
            "Authorization recommendations are "
            "classification-driven, deterministic, "
            "and included in decision intelligence."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
