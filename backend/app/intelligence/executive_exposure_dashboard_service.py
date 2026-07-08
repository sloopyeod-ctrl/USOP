from sqlalchemy.orm import Session

from app.analytics.access_analyzer import AccessAnalyzer
from app.exposure.exposure_score_engine import ExposureScoreEngine
from app.graph.identity_graph_service import IdentityGraphService
from app.models.identity import Identity
from app.recommendations.recommendation_engine import RecommendationEngine


class ExecutiveExposureDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.access_analyzer = AccessAnalyzer(db)
        self.graph_service = IdentityGraphService(db)
        self.exposure_engine = ExposureScoreEngine()
        self.recommendation_engine = RecommendationEngine()

    def dashboard(self):
        identities = (
            self.db.query(Identity)
            .filter(Identity.is_active == True)
            .all()
        )

        risks = self.access_analyzer.identity_risk()

        summary = {
            "total_identities": len(identities),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        top_risks = []

        for identity in identities:
            graph = self.graph_service.get_identity_graph(identity.id)

            identity_risk = next(
                (
                    risk
                    for risk in risks
                    if risk["identity_id"] == identity.id
                ),
                None,
            )

            exposure = self.exposure_engine.calculate(
                graph,
                identity_risk,
            )

            findings = identity_risk["findings"] if identity_risk else []

            recommendations = self.recommendation_engine.generate(findings)

            rating = exposure["rating"].lower()

            if rating == "critical":
                summary["critical"] += 1
            elif rating == "high":
                summary["high"] += 1
            elif rating == "medium":
                summary["medium"] += 1
            else:
                summary["low"] += 1

            policy_violations = len(
                [
                    finding
                    for finding in findings
                    if finding["type"] == "policy_violation"
                ]
            )

            top_risks.append(
                {
                    "identity_id": identity.id,
                    "display_name": identity.display_name,
                    "primary_email": identity.primary_email,
                    "exposure_score": exposure["score"],
                    "exposure_rating": exposure["rating"],
                    "risk_score": identity_risk["risk_score"] if identity_risk else 0,
                    "risk_level": identity_risk["risk_level"] if identity_risk else "Low",
                    "recommendation_count": len(recommendations),
                    "policy_violations": policy_violations,
                }
            )

        top_risks.sort(
            key=lambda item: (
                -item["exposure_score"],
                -item["risk_score"],
            )
        )

        return {
            "summary": summary,
            "top_risks": top_risks[:10],
        }