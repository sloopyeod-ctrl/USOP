from sqlalchemy.orm import Session

from app.connectors.manager.ConnectorManager import ConnectorManager
from app.connectors.microsoft.EntraProvider import EntraProvider
from app.reconciliation.reconciliation_engine import ReconciliationEngine
from app.services.audit_service import AuditService
from app.synchronization.models.SynchronizationResult import (
    SynchronizationResult,
)
from app.synchronization.normalization import NormalizationEngine


class SynchronizationEngine:
    """
    Executes provider collection, normalization, and reconciliation.

    Identity-specific graph comparison will be reintroduced in a later
    milestone after affected identities can be resolved dynamically.
    """

    def __init__(self, db: Session):
        self.db = db

        self.connector_manager = ConnectorManager()
        self.connector_manager.register(EntraProvider())

        self.audit_service = AuditService(db)
        self.normalizer = NormalizationEngine()
        self.reconciliation_engine = ReconciliationEngine(db)

    @staticmethod
    def _count_collections(data: dict) -> dict[str, int]:
        return {
            key: len(value)
            for key, value in data.items()
            if isinstance(value, list)
        }

    @staticmethod
    def _extract_operation_counts(
        reconciliation: dict,
        operation: str,
    ) -> dict[str, int]:
        suffix = f"_{operation}"

        return {
            key.removesuffix(suffix): value
            for key, value in reconciliation.items()
            if key.endswith(suffix)
        }

    def run(self, connector_name: str) -> dict:
        result = SynchronizationResult(
            provider_name=connector_name,
            status="running",
        )

        provider = self.connector_manager.get(connector_name)

        if provider is None:
            result.status = "failed"
            result.errors.append("Connector provider not found.")
            result.metadata["available_connectors"] = list(
                self.connector_manager.providers()
            )

            return result.complete().to_dict()

        try:
            collected = provider.collect()
            result.collected = self._count_collections(collected)

            normalized = self.normalizer.normalize(
                connector_name,
                collected,
            )
            result.normalized = self._count_collections(normalized)

            reconciliation = self.reconciliation_engine.reconcile(
                normalized
            )

            result.reconciled = reconciliation
            result.created = self._extract_operation_counts(
                reconciliation,
                "created",
            )
            result.updated = self._extract_operation_counts(
                reconciliation,
                "updated",
            )

            result.status = "success"
            result.metadata["provider"] = provider.provider_name
            result.metadata["graph_processing"] = "deferred"

            result.complete()

            self.audit_service.record(
                event_type="SynchronizationCompleted",
                entity_type="Connector",
                entity_id=connector_name,
                actor="USOP Sync Engine",
                message=(
                    f"Synchronization completed for {connector_name}."
                ),
                metadata=result.to_dict(),
            )

            return result.to_dict()

        except Exception as exc:
            self.db.rollback()

            result.status = "failed"
            result.errors.append(str(exc))
            result.metadata["provider"] = provider.provider_name

            return result.complete().to_dict()
