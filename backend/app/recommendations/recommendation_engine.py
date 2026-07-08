class RecommendationEngine:
    def generate(self, findings: list):
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
                }

            elif finding["type"] == "policy_violation":
                recommendation = {
                    "priority": 1,
                    "severity": "Critical",
                    "title": "Remediate Policy Violation",
                    "description": (
                        f"Resolve policy "
                        f"{finding['policy_name']}."
                    ),
                    "risk_reduction": 30,
                    "estimated_effort": "15 minutes",
                }

            elif finding["type"] == "privileged_group":
                recommendation = {
                    "priority": 2,
                    "severity": "High",
                    "title": "Review Privileged Membership",
                    "description": (
                        f"Validate membership in "
                        f"{finding['group_name']}."
                    ),
                    "risk_reduction": 25,
                    "estimated_effort": "10 minutes",
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
                }

            if recommendation:
                recommendations.append(recommendation)

        recommendations.sort(
            key=lambda x: (
                x["priority"],
                -x["risk_reduction"],
            )
        )

        return recommendations