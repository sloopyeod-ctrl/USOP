from sqlalchemy.orm import Session

from app.services.audit_service import AuditService
from app.services.connector_service import ConnectorService
from app.synchronization.normalization import NormalizationEngine
from app.reconciliation.reconciliation_engine import ReconciliationEngine
from app.graph.identity_graph_service import IdentityGraphService
from app.graph.graph_difference_engine import GraphDifferenceEngine


class SynchronizationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.connector_service = ConnectorService()
        self.audit_service = AuditService(db)
        self.normalizer = NormalizationEngine()
        self.reconciliation_engine = ReconciliationEngine(db)
        self.graph_service = IdentityGraphService(db)
        self.diff_engine = GraphDifferenceEngine(db)

    def run(self, connector_name: str):
        collected = self.connector_service.collect(connector_name)

        if collected is None:
            return {
                "status": "failed",
                "connector": connector_name,
                "reason": "Connector not found",
            }

        normalized = self.normalizer.normalize(
            connector_name,
            collected,
        )

        before_graph = self.graph_service.get_identity_graph(
            "ed8b8386-22fe-4d95-bf82-7071163bb4d0"
        )

        reconciliation = self.reconciliation_engine.reconcile(normalized)

        after_graph = self.graph_service.get_identity_graph(
            "ed8b8386-22fe-4d95-bf82-7071163bb4d0"
        )

        changes = self.diff_engine.compare(
            before_graph,
            after_graph,
        )

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
            "normalized": normalized,
            "reconciliation": reconciliation,
            "changes": changes,
        }