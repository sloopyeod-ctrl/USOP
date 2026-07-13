from sqlalchemy.orm import Session

from app.analytics.access_analyzer import AccessAnalyzer
from app.exposure.exposure_score_engine import (
    ExposureScoreEngine,
)
from app.graph.identity_graph_service import (
    IdentityGraphService,
)
from app.intelligence.identity_decision_service import (
    IdentityDecisionService,
)
from app.recommendations.recommendation_engine import (
    RecommendationEngine,
)
from app.security.authorization import (
    AuthorizationClassificationService,
)
from app.timeline.identity_timeline_builder import (
    IdentityTimelineBuilder,
)


class IdentityIntelligenceService:
    def __init__(self, db: Session):
        self.db = db
        self.graph_service = IdentityGraphService(db)
        self.access_analyzer = AccessAnalyzer(db)
        self.timeline_builder = IdentityTimelineBuilder(db)
        self.recommendation_engine = RecommendationEngine()
        self.exposure_engine = ExposureScoreEngine()
        self.authorization_classifier = (
            AuthorizationClassificationService()
        )
        self.decision_service = IdentityDecisionService()

    def get_identity_intelligence(
        self,
        identity_id: str,
    ):
        graph = self.graph_service.get_identity_graph(
            identity_id
        )

        if graph is None:
            return None

        risks = self.access_analyzer.identity_risk()

        identity_risk = next(
            (
                risk
                for risk in risks
                if risk["identity_id"]
                == identity_id
            ),
            None,
        )

        timeline = self.timeline_builder.build(
            identity_id
        )

        exposure = self.exposure_engine.calculate(
            graph,
            identity_risk,
        )

        authorization_classifications = [
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

        findings = (
            identity_risk["findings"]
            if identity_risk
            else []
        )

        recommendations = (
            self.recommendation_engine.generate(
                findings=findings,
                authorization_classifications=(
                    authorization_classifications
                ),
            )
        )

        decision = self.decision_service.build(
            graph=graph,
            identity_risk=identity_risk,
            exposure=exposure,
            recommendations=recommendations,
            role_classifications=(
                authorization_classifications
            ),
        )

        return {
            "identity": graph["identity"],
            "risk": {
                "score": (
                    identity_risk["risk_score"]
                    if identity_risk
                    else 0
                ),
                "level": (
                    identity_risk["risk_level"]
                    if identity_risk
                    else "Low"
                ),
                "findings": findings,
            },
            "exposure": exposure,
            "access": {
                "accounts": graph["accounts"],
                "groups": graph["groups"],
                "roles": graph["roles"],
            },
            "timeline": timeline,
            "recommendations": recommendations,
            "decision": decision,
        }
