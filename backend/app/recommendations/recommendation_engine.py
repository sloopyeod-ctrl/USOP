import hashlib
import json
from typing import Any


class RecommendationEngine:
    """
    Generate deterministic remediation recommendations from risk findings and
    canonical authorization classifications.

    Authorization recommendations rely on classification output rather than
    loose role-name matching.

    Every recommendation receives a deterministic backend-owned identifier.
    The identifier remains stable across sorting and regeneration while the
    recommendation's canonical security meaning remains unchanged.
    """

    RECOMMENDATION_ID_VERSION = "rec_v1"

    def generate(
        self,
        findings: list[dict[str, Any]],
        authorization_classifications: (
            list[dict[str, Any]] | None
        ) = None,
    ) -> list[dict[str, Any]]:
        recommendations = []

        recommendations.extend(
            self._finding_recommendations(findings)
        )

        recommendations.extend(
            self._authorization_recommendations(
                authorization_classifications or []
            )
        )

        recommendations = [
            self._with_recommendation_id(
                recommendation
            )
            for recommendation in recommendations
        ]

        recommendations.sort(
            key=lambda item: (
                item.get("priority", 999),
                -item.get("risk_reduction", 0),
                item.get("title", ""),
                item.get("recommendation_id", ""),
            )
        )

        return recommendations

    def _with_recommendation_id(
        self,
        recommendation: dict[str, Any],
    ) -> dict[str, Any]:
        canonical_payload = {
            "recommendation_type": (
                recommendation.get(
                    "recommendation_type"
                )
            ),
            "evidence_type": recommendation.get(
                "evidence_type"
            ),
            "title": recommendation.get("title"),
            "description": recommendation.get(
                "description"
            ),
            "role_name": recommendation.get(
                "role_name"
            ),
            "capability": recommendation.get(
                "capability"
            ),
            "scope_classification": (
                recommendation.get(
                    "scope_classification"
                )
            ),
            "assignment_classification": (
                recommendation.get(
                    "assignment_classification"
                )
            ),
        }

        serialized_payload = json.dumps(
            canonical_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            serialized_payload.encode("utf-8")
        ).hexdigest()[:24]

        return {
            **recommendation,
            "recommendation_id": (
                f"{self.RECOMMENDATION_ID_VERSION}_"
                f"{digest}"
            ),
        }

    def _finding_recommendations(
        self,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        recommendations = []

        for finding in findings:
            recommendation = None

            if finding["type"] == "weak_authentication":
                recommendation = {
                    "priority": 1,
                    "severity": "High",
                    "title": "Enable MFA",
                    "description": (
                        f"Enable MFA for account "
                        f"{finding['username']}."
                    ),
                    "risk_reduction": 20,
                    "estimated_effort": "5 minutes",
                    "recommendation_type": (
                        "Authentication"
                    ),
                    "evidence_type": finding["type"],
                }

            elif finding["type"] == "policy_violation":
                recommendation = {
                    "priority": 1,
                    "severity": "Critical",
                    "title": (
                        "Remediate Policy Violation"
                    ),
                    "description": (
                        f"Resolve policy "
                        f"{finding['policy_name']}."
                    ),
                    "risk_reduction": 30,
                    "estimated_effort": "15 minutes",
                    "recommendation_type": "Policy",
                    "evidence_type": finding["type"],
                }

            elif finding["type"] == "privileged_group":
                recommendation = {
                    "priority": 2,
                    "severity": "High",
                    "title": (
                        "Review Privileged Membership"
                    ),
                    "description": (
                        f"Validate membership in "
                        f"{finding['group_name']}."
                    ),
                    "risk_reduction": 25,
                    "estimated_effort": "10 minutes",
                    "recommendation_type": (
                        "Authorization"
                    ),
                    "evidence_type": finding["type"],
                }

            elif finding["type"] == "dormant_account":
                recommendation = {
                    "priority": 2,
                    "severity": "Medium",
                    "title": "Disable Dormant Account",
                    "description": (
                        f"Review dormant account "
                        f"{finding['username']}."
                    ),
                    "risk_reduction": 15,
                    "estimated_effort": "2 minutes",
                    "recommendation_type": (
                        "AccountLifecycle"
                    ),
                    "evidence_type": finding["type"],
                }

            if recommendation:
                recommendations.append(
                    recommendation
                )

        return recommendations

    def _authorization_recommendations(
        self,
        classifications: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        recommendations = []

        for item in classifications:
            role = item.get("role", {})
            classification = item.get(
                "classification",
                {},
            )

            risk_level = classification.get(
                "risk_level",
                "Unknown",
            )

            if risk_level not in {
                "Critical",
                "High",
            }:
                continue

            role_name = (
                role.get("role_name")
                or "Privileged Role"
            )

            capability = classification.get(
                "capability",
                "Unclassified",
            )

            scope = classification.get(
                "scope_classification",
                "Unknown",
            )

            assignment = classification.get(
                "assignment_classification",
                "Unknown",
            )

            if risk_level == "Critical":
                priority = 1
                severity = "Critical"
                risk_reduction = 30
                estimated_effort = "15 minutes"
            else:
                priority = 2
                severity = "High"
                risk_reduction = 20
                estimated_effort = "10 minutes"

            scope_text = {
                "TenantWide": "tenant-wide",
                "DirectoryScoped": (
                    "directory-scoped"
                ),
                "ApplicationScoped": (
                    "application-scoped"
                ),
                "Unknown": "unconfirmed-scope",
            }.get(
                scope,
                "unconfirmed-scope",
            )

            recommendations.append(
                {
                    "priority": priority,
                    "severity": severity,
                    "title": (
                        f"Review {role_name} Assignment"
                    ),
                    "description": (
                        "Validate the continued business "
                        "need for the "
                        f"{assignment.lower()} "
                        f"{scope_text} "
                        f"{role_name} assignment."
                    ),
                    "risk_reduction": risk_reduction,
                    "estimated_effort": (
                        estimated_effort
                    ),
                    "recommendation_type": (
                        "Authorization"
                    ),
                    "evidence_type": (
                        "CanonicalRoleClassification"
                    ),
                    "role_name": role_name,
                    "capability": capability,
                    "scope_classification": scope,
                    "assignment_classification": (
                        assignment
                    ),
                    "classification_source": (
                        classification.get(
                            "classification_source"
                        )
                    ),
                }
            )

        return recommendations