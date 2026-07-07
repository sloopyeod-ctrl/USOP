from sqlalchemy.orm import Session

from app.services.audit_service import AuditService
from app.services.connector_service import ConnectorService


class SynchronizationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.connector_service = ConnectorService()
        self.audit_service = AuditService(db)

    def run(self, connector_name: str):
        collected = self.connector_service.collect(connector_name)

        if collected is None:
            return {
                "status": "failed",
                "connector": connector_name,
                "reason": "Connector not found",
            }

        summary = {
            "identities": len(collected.get("identities", [])),
            "accounts": len(collected.get("accounts", [])),
            "groups": len(collected.get("groups", [])),
            "roles": len(collected.get("roles", [])),
        }

        self.audit_service.record(
            event_type="SynchronizationCompleted",
            entity_type="Connector",
            entity_id=connector_name,
            actor="USOP Sync Engine",
            message=f"Synchronization completed for {connector_name}.",
            metadata={
                "connector": connector_name,
                "summary": summary,
            },
        )

        return {
            "status": "completed",
            "connector": connector_name,
            "summary": summary,
            "collected": collected,
        }