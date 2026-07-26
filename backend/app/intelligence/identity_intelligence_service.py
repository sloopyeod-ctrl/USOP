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
from app.intelligence.recommendation_disposition_service import (
    RecommendationDispositionService,
)
from app.recommendations.recommendation_engine import (
    RecommendationEngine,
)
from app.repositories.decision_record_repository import (
    DecisionRecordRepository,
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
        self.decision_record_repository = (
            DecisionRecordRepository(db)
        )
        self.disposition_service = (
            RecommendationDispositionService()
        )

    def get_identity_intelligence(
        self,
        identity_id: str,
        organization_id: str | None = None,
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

        if organization_id:
            decision_records = (
                self.decision_record_repository
                .by_identity(
                    organization_id=organization_id,
                    identity_id=identity_id,
                )
            )

            recommendations = (
                self.disposition_service.project(
                    recommendations=recommendations,
                    decision_records=decision_records,
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
