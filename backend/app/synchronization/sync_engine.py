from sqlalchemy.orm import Session

from app.connectors.manager.ConnectorManager import ConnectorManager
from app.connectors.microsoft.EntraProvider import EntraProvider
from app.services.audit_service import AuditService
from app.synchronization.normalization import NormalizationEngine
from app.reconciliation.reconciliation_engine import ReconciliationEngine
from app.graph.identity_graph_service import IdentityGraphService
from app.graph.graph_difference_engine import GraphDifferenceEngine
from app.events.change_event_engine import ChangeEventEngine


class SynchronizationEngine:
    def __init__(self, db: Session):
        self.db = db

        self.connector_manager = ConnectorManager()
        self.connector_manager.register(EntraProvider())

        self.audit_service = AuditService(db)
        self.normalizer = NormalizationEngine()
        self.reconciliation_engine = ReconciliationEngine(db)
        self.graph_service = IdentityGraphService(db)
        self.diff_engine = GraphDifferenceEngine(db)
        self.change_event_engine = ChangeEventEngine(db)

    def run(self, connector_name: str):
        provider = self.connector_manager.get(connector_name)

        if provider is None:
            return {
                "status": "failed",
                "connector": connector_name,
                "reason": "Connector provider not found",
                "available_connectors": list(self.connector_manager.providers()),
            }

        collected = provider.collect()

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

        events_generated = self.change_event_engine.generate(
            "ed8b8386-22fe-4d95-bf82-7071163bb4d0",
            changes,
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
                "provider": provider.provider_name,
            },
        )

        return {
            "status": "completed",
            "connector": connector_name,
            "provider": provider.provider_name,
            "summary": summary,
            "normalized": normalized,
            "reconciliation": reconciliation,
            "changes": changes,
            "events_generated": events_generated,
        }