from sqlalchemy.orm import Session

from app.analytics.access_analyzer import AccessAnalyzer
from app.graph.identity_graph_service import IdentityGraphService
from app.timeline.identity_timeline_builder import IdentityTimelineBuilder


class IdentityIntelligenceService:
    def __init__(self, db: Session):
        self.db = db
        self.graph_service = IdentityGraphService(db)
        self.access_analyzer = AccessAnalyzer(db)
        self.timeline_builder = IdentityTimelineBuilder(db)

    def get_identity_intelligence(self, identity_id: str):
        graph = self.graph_service.get_identity_graph(identity_id)

        if graph is None:
            return None

        risks = self.access_analyzer.identity_risk()

        identity_risk = next(
            (
                risk
                for risk in risks
                if risk["identity_id"] == identity_id
            ),
            None,
        )

        timeline = self.timeline_builder.build(identity_id)

        recommendations = []

        if identity_risk:
            for finding in identity_risk.get("findings", []):
                if finding["type"] == "weak_authentication":
                    recommendations.append(
                        f"Review weak authentication for {finding.get('username')}."
                    )

                if finding["type"] == "dormant_account":
                    recommendations.append(
                        f"Review dormant account {finding.get('username')}."
                    )

                if finding["type"] == "privileged_group":
                    recommendations.append(
                        f"Validate privileged group membership: {finding.get('group_name')}."
                    )

                if finding["type"] == "policy_violation":
                    recommendations.append(
                        f"Remediate policy violation: {finding.get('policy_name')}."
                    )

        return {
            "identity": graph["identity"],
            "risk": {
                "score": identity_risk["risk_score"] if identity_risk else 0,
                "level": identity_risk["risk_level"] if identity_risk else "Low",
                "findings": identity_risk["findings"] if identity_risk else [],
            },
            "access": {
                "accounts": graph["accounts"],
                "groups": graph["groups"],
                "roles": graph["roles"],
            },
            "timeline": timeline,
            "recommendations": recommendations,
        }