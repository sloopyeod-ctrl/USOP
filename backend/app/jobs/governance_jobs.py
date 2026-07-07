from sqlalchemy.orm import Session

from app.analytics.access_analyzer import AccessAnalyzer
from app.services.audit_service import AuditService
from app.services.connector_service import ConnectorService


class GovernanceJobs:
    def __init__(self, db: Session):
        self.db = db
        self.access_analyzer = AccessAnalyzer(db)
        self.audit_service = AuditService(db)
        self.connector_service = ConnectorService()

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
    
    def run_connector_sync(self, connector_name: str):
        result = self.connector_service.synchronize(connector_name)

        if result is None:
            return {
                "job": "connector-sync",
                "status": "failed",
                "connector": connector_name,
                "reason": "Connector not found",
            }

        self.audit_service.record(
            event_type="JobCompleted",
            entity_type="GovernanceJob",
            entity_id=f"connector-sync:{connector_name}",
            actor="USOP Job Engine",
            message=f"Connector sync job completed for {connector_name}.",
            metadata={
                "job_name": "connector-sync",
                "connector": connector_name,
                "result": result,
            },
        )

        return {
            "job": "connector-sync",
            "status": "completed",
            "connector": connector_name,
            "result": result,
        }