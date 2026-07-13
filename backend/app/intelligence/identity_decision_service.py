from typing import Any

from app.security.authorization import (
    AuthorizationClassificationService,
)


class IdentityDecisionService:
    """
    Assemble existing identity-security conclusions into one explainable
    decision object.

    This service does not query providers or independently calculate identity
    risk. It orchestrates canonical graph evidence, risk, exposure,
    authorization classification, and deterministic recommendations.
    """

    SEVERITY_ORDER = {
        "Unknown": 0,
        "Low": 1,
        "Moderate": 2,
        "Medium": 2,
        "High": 3,
        "Critical": 4,
    }

    FORBIDDEN_EVIDENCE_FIELDS = {
        "access_token",
        "refresh_token",
        "client_secret",
        "password",
        "credential",
        "credentials",
        "secret",
        "raw_payload",
    }

    def __init__(self):
        self.authorization_classifier = (
            AuthorizationClassificationService()
        )

    def build(
        self,
        graph: dict[str, Any],
        identity_risk: dict[str, Any] | None,
        exposure: dict[str, Any],
        recommendations: list[dict[str, Any]],
        role_classifications: (
            list[dict[str, Any]] | None
        ) = None,
    ) -> dict[str, Any]:
        role_classifications = (
            role_classifications
            if role_classifications is not None
            else [
            {
                "role": role,
                "classification": (
                    self.authorization_classifier.classify(
                        role
                    )
                ),
            }
                for role in graph.get("roles", [])
            ]
        )

        priority = self._priority(
            identity_risk=identity_risk,
            exposure=exposure,
            role_classifications=role_classifications,
        )

        confidence = self._confidence(
            graph=graph,
            identity_risk=identity_risk,
            exposure=exposure,
        )

        authorization_summary = (
            self._authorization_summary(
                graph=graph,
                role_classifications=role_classifications,
            )
        )

        evidence = self._evidence(
            graph=graph,
            role_classifications=role_classifications,
        )

        summary = self._summary(
            graph=graph,
            priority=priority,
            authorization_summary=authorization_summary,
        )

        next_step = self._next_step(
            recommendations=recommendations,
            role_classifications=role_classifications,
        )

        return {
            "available": True,
            "priority": priority,
            "summary": summary,
            "confidence": confidence,
            "authorization": authorization_summary,
            "evidence": evidence,
            "recommended_actions": recommendations,
            "next_step": next_step,
            "estimated_effort": (
                self._estimated_effort(
                    recommendations
                )
            ),
            "estimated_risk_reduction": (
                self._estimated_risk_reduction(
                    recommendations
                )
            ),
        }

    def _priority(
        self,
        identity_risk: dict[str, Any] | None,
        exposure: dict[str, Any],
        role_classifications: list[dict[str, Any]],
    ) -> str:
        candidates = [
            exposure.get("rating", "Unknown"),
            (
                identity_risk.get(
                    "risk_level",
                    "Unknown",
                )
                if identity_risk
                else "Unknown"
            ),
        ]

        candidates.extend(
            item["classification"].get(
                "risk_level",
                "Unknown",
            )
            for item in role_classifications
        )

        return max(
            candidates,
            key=lambda value: self.SEVERITY_ORDER.get(
                str(value),
                0,
            ),
        )

    def _confidence(
        self,
        graph: dict[str, Any],
        identity_risk: dict[str, Any] | None,
        exposure: dict[str, Any],
    ) -> dict[str, Any]:
        score = 0
        basis = []
        gaps = []

        if graph.get("identity"):
            score += 15
            basis.append(
                "Canonical identity record is available."
            )
        else:
            gaps.append(
                "Canonical identity record is unavailable."
            )

        if graph.get("accounts"):
            score += 15
            basis.append(
                "At least one active account is available."
            )
        else:
            gaps.append(
                "No active accounts are available."
            )

        if graph.get("groups"):
            score += 10
            basis.append(
                "Canonical group memberships are available."
            )
        else:
            gaps.append(
                "No group-membership evidence is available."
            )

        roles = graph.get("roles", [])

        if roles:
            score += 15
            basis.append(
                "Canonical role assignments are available."
            )
        else:
            gaps.append(
                "No role-assignment evidence is available."
            )

        role_evidence_complete = bool(roles) and all(
            role.get("assignment_type")
            and (
                role.get("directory_scope")
                or role.get("application_scope")
            )
            for role in roles
        )

        if role_evidence_complete:
            score += 20
            basis.append(
                "Role assignment type and scope evidence "
                "are complete."
            )
        elif roles:
            gaps.append(
                "Some role assignments lack type or scope "
                "evidence."
            )

        if identity_risk is not None:
            score += 15
            basis.append(
                "Current deterministic identity-risk "
                "analysis is available."
            )
        else:
            gaps.append(
                "Identity-risk analysis is unavailable."
            )

        if exposure:
            score += 10
            basis.append(
                "Current exposure analysis is available."
            )
        else:
            gaps.append(
                "Exposure analysis is unavailable."
            )

        return {
            "score": min(score, 100),
            "basis": basis,
            "gaps": gaps,
        }

    def _authorization_summary(
        self,
        graph: dict[str, Any],
        role_classifications: list[dict[str, Any]],
    ) -> dict[str, Any]:
        privileged_roles = [
            item
            for item in role_classifications
            if item["classification"].get(
                "risk_level"
            )
            in {"Critical", "High"}
        ]

        tenant_wide_roles = [
            item
            for item in role_classifications
            if item["classification"].get(
                "scope_classification"
            )
            == "TenantWide"
        ]

        direct_roles = [
            item
            for item in role_classifications
            if item["classification"].get(
                "assignment_classification"
            )
            == "Direct"
        ]

        privileged_groups = [
            group
            for group in graph.get("groups", [])
            if str(
                group.get("privilege_level") or ""
            ).lower()
            in {
                "critical",
                "privileged",
                "high",
                "admin",
                "administrator",
                "owner",
            }
        ]

        return {
            "account_count": len(
                graph.get("accounts", [])
            ),
            "group_count": len(
                graph.get("groups", [])
            ),
            "role_count": len(
                graph.get("roles", [])
            ),
            "privileged_group_count": len(
                privileged_groups
            ),
            "privileged_role_count": len(
                privileged_roles
            ),
            "tenant_wide_assignment_count": len(
                tenant_wide_roles
            ),
            "direct_assignment_count": len(
                direct_roles
            ),
            "role_classifications": [
                {
                    "role_name": item["role"].get(
                        "role_name"
                    ),
                    "risk_level": (
                        item["classification"].get(
                            "risk_level"
                        )
                    ),
                    "capability": (
                        item["classification"].get(
                            "capability"
                        )
                    ),
                    "scope": (
                        item["classification"].get(
                            "scope_classification"
                        )
                    ),
                    "assignment": (
                        item["classification"].get(
                            "assignment_classification"
                        )
                    ),
                    "classification_source": (
                        item["classification"].get(
                            "classification_source"
                        )
                    ),
                    "reasons": (
                        item["classification"].get(
                            "reasons",
                            [],
                        )
                    ),
                }
                for item in role_classifications
            ],
        }

    def _evidence(
        self,
        graph: dict[str, Any],
        role_classifications: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        evidence = []

        for account in graph.get("accounts", []):
            evidence.append(
                {
                    "type": "Account",
                    "title": account.get(
                        "username"
                    ),
                    "facts": {
                        "system_name": account.get(
                            "system_name"
                        ),
                        "account_type": account.get(
                            "account_type"
                        ),
                        "status": account.get(
                            "status"
                        ),
                        "mfa_enabled": account.get(
                            "mfa_enabled"
                        ),
                    },
                }
            )

        for group in graph.get("groups", []):
            evidence.append(
                {
                    "type": "GroupMembership",
                    "title": group.get(
                        "group_name"
                    ),
                    "facts": {
                        "membership_type": group.get(
                            "membership_type"
                        ),
                        "system_name": group.get(
                            "system_name"
                        ),
                        "privilege_level": group.get(
                            "privilege_level"
                        ),
                    },
                }
            )

        for item in role_classifications:
            role = item["role"]
            classification = item[
                "classification"
            ]

            evidence.append(
                {
                    "type": "RoleAssignment",
                    "title": role.get(
                        "role_name"
                    ),
                    "facts": {
                        "risk_level": (
                            classification.get(
                                "risk_level"
                            )
                        ),
                        "capability": (
                            classification.get(
                                "capability"
                            )
                        ),
                        "assignment_type": (
                            role.get(
                                "assignment_type"
                            )
                        ),
                        "directory_scope": (
                            role.get(
                                "directory_scope"
                            )
                        ),
                        "application_scope": (
                            role.get(
                                "application_scope"
                            )
                        ),
                        "classification_source": (
                            classification.get(
                                "classification_source"
                            )
                        ),
                    },
                }
            )

        return [
            self._sanitize_evidence(item)
            for item in evidence
        ]

    def _summary(
        self,
        graph: dict[str, Any],
        priority: str,
        authorization_summary: dict[str, Any],
    ) -> dict[str, str]:
        identity_name = (
            graph.get("identity", {}).get(
                "display_name"
            )
            or "This identity"
        )

        privileged_roles = (
            authorization_summary[
                "privileged_role_count"
            ]
        )
        tenant_wide = (
            authorization_summary[
                "tenant_wide_assignment_count"
            ]
        )

        if privileged_roles and tenant_wide:
            title = (
                "Tenant-wide privileged identity"
            )
            description = (
                f"{identity_name} has "
                f"{privileged_roles} high-impact role "
                f"assignment(s), including "
                f"{tenant_wide} tenant-wide assignment(s)."
            )
        elif privileged_roles:
            title = "Privileged identity"
            description = (
                f"{identity_name} has "
                f"{privileged_roles} high-impact role "
                "assignment(s)."
            )
        elif authorization_summary["role_count"]:
            title = "Authorized identity"
            description = (
                f"{identity_name} has "
                f"{authorization_summary['role_count']} "
                "active role assignment(s)."
            )
        else:
            title = "Limited authorization evidence"
            description = (
                f"{identity_name} currently has no active "
                "role assignments in the canonical graph."
            )

        return {
            "title": title,
            "description": description,
            "priority_statement": (
                f"Overall decision priority is "
                f"{priority}."
            ),
        }

    def _next_step(
        self,
        recommendations: list[dict[str, Any]],
        role_classifications: list[dict[str, Any]],
    ) -> str:
        if recommendations:
            top_recommendation = min(
                recommendations,
                key=lambda item: (
                    item.get("priority", 999),
                    -item.get(
                        "risk_reduction",
                        0,
                    ),
                ),
            )

            return (
                top_recommendation.get(
                    "description"
                )
                or top_recommendation.get(
                    "title"
                )
                or "Review the highest-priority finding."
            )

        high_impact_roles = [
            item
            for item in role_classifications
            if item["classification"].get(
                "risk_level"
            )
            in {"Critical", "High"}
        ]

        if high_impact_roles:
            role_name = high_impact_roles[
                0
            ]["role"].get(
                "role_name",
                "privileged role",
            )

            return (
                f"Validate the continued business need "
                f"and assignment scope for {role_name}."
            )

        return (
            "Review the available authorization evidence "
            "and confirm access remains appropriate."
        )

    @staticmethod
    def _estimated_effort(
        recommendations: list[dict[str, Any]],
    ) -> str:
        if not recommendations:
            return "Requires analyst review"

        efforts = [
            recommendation.get(
                "estimated_effort"
            )
            for recommendation in recommendations
            if recommendation.get(
                "estimated_effort"
            )
        ]

        if not efforts:
            return "Requires analyst review"

        if len(efforts) == 1:
            return efforts[0]

        return (
            f"{len(efforts)} recommended actions; "
            "effort varies by remediation."
        )

    @staticmethod
    def _estimated_risk_reduction(
        recommendations: list[dict[str, Any]],
    ) -> int:
        return min(
            sum(
                int(
                    recommendation.get(
                        "risk_reduction",
                        0,
                    )
                )
                for recommendation in recommendations
            ),
            100,
        )

    def _sanitize_evidence(
        self,
        value: Any,
    ) -> Any:
        if isinstance(value, dict):
            return {
                key: self._sanitize_evidence(
                    child
                )
                for key, child in value.items()
                if str(key).lower()
                not in self.FORBIDDEN_EVIDENCE_FIELDS
            }

        if isinstance(value, list):
            return [
                self._sanitize_evidence(child)
                for child in value
            ]

        return value
