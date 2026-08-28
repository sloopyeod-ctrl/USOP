from typing import Any

from sqlalchemy.orm import Session

from app.models.authorization_event import AuthorizationEvent
from app.services.pending_decision_work_item_service import (
    PendingDecisionWorkItemService,
)


SYSTEM_AUTHORIZATION_WORK_ACTOR = (
    "system:authorization-work-generator"
)


class AuthorizationWorkItemGenerator:
    """Create generic analyst work from material AuthorizationEvents."""

    def __init__(
        self,
        db: Session,
        *,
        work_item_service: (
            PendingDecisionWorkItemService | None
        ) = None,
    ):
        self.work_item_service = (
            work_item_service
            or PendingDecisionWorkItemService(db)
        )

    @staticmethod
    def _classification(
        event: AuthorizationEvent,
    ) -> dict[str, Any]:
        evidence = event.evidence_json or {}
        value = evidence.get("classification")
        return value if isinstance(value, dict) else {}

    @classmethod
    def _role_label(
        cls,
        event: AuthorizationEvent,
    ) -> str:
        classification = cls._classification(event)
        safe_evidence = classification.get("evidence")

        if isinstance(safe_evidence, dict):
            role_name = safe_evidence.get("role_name")
            if isinstance(role_name, str) and role_name.strip():
                return role_name.strip()

        capability = classification.get("capability")
        if isinstance(capability, str) and capability.strip():
            return capability.strip()

        return "authorization"

    @classmethod
    def _title(cls, event: AuthorizationEvent) -> str:
        label = cls._role_label(event)

        if event.event_type == "ROLE_ASSIGNED":
            return f"Review {label} assignment"

        if event.event_type == "ROLE_UPDATED":
            return f"Review {label} change"

        return "Review material authorization event"

    @staticmethod
    def _materiality_reason(
        event: AuthorizationEvent,
    ) -> str:
        reasons = (event.evidence_json or {}).get("reasons")

        if isinstance(reasons, list):
            normalized = [
                str(reason).strip()
                for reason in reasons
                if str(reason).strip()
            ]
            if normalized:
                return " ".join(normalized)

        return (
            "Authorization event was classified as material "
            "and requires human review."
        )

    @classmethod
    def _snapshot(
        cls,
        event: AuthorizationEvent,
    ) -> dict[str, Any]:
        classification = cls._classification(event)

        return {
            "authorization_event_id": event.id,
            "event_type": event.event_type,
            "detected_at": event.detected_at.isoformat(),
            "risk_level": event.risk_level,
            "is_material": event.is_material,
            "role_name": cls._role_label(event),
            "capability": classification.get("capability"),
            "classification_source": (
                classification.get("classification_source")
            ),
            "scope_classification": (
                classification.get("scope_classification")
            ),
            "assignment_classification": (
                classification.get("assignment_classification")
            ),
        }

    def generate(
        self,
        *,
        event: AuthorizationEvent,
    ):
        if not event.is_material:
            return None

        return self.work_item_service.create_pending(
            organization_id=event.organization_id,
            identity_id=event.identity_id,
            source_type="AuthorizationEvent",
            source_id=event.id,
            decision_category="Authorization",
            title=self._title(event),
            summary=(
                f"{event.event_type} authorization evidence "
                "requires analyst judgment."
            ),
            priority=event.risk_level,
            risk_level=event.risk_level,
            materiality_reason=self._materiality_reason(event),
            evidence_snapshot_json=self._snapshot(event),
            source_system="USOP",
            source_identifier=event.id,
            confidence_score=event.confidence_score,
            actor=SYSTEM_AUTHORIZATION_WORK_ACTOR,
        )
