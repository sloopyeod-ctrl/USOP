from sqlalchemy.orm import Session

from app.analytics.access_analyzer import AccessAnalyzer
from app.services.audit_service import AuditService


class GovernanceJobs:
    def __init__(self, db: Session):
        self.db = db
        self.access_analyzer = AccessAnalyzer(db)
        self.audit_service = AuditService(db)

    def run_identity_risk_analysis(self):
        results = self.access_analyzer.identity_risk()

        self.audit_service.record(
            event_type="JobCompleted",
            entity_type="GovernanceJob",
            entity_id="identity-risk-analysis",
            actor="USOP Job Engine",
            message="Identity risk analysis job completed.",
            metadata={
                "job_name": "identity-risk-analysis",
                "identity_count": len(results),
            },
        )

        return {
            "job": "identity-risk-analysis",
            "status": "completed",
            "identity_count": len(results),
            "results": results,
        }