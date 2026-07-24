from typing import Any

from sqlalchemy.orm import Session

from app.domain import (
    ApprovalStatus,
    DecisionStatus,
    DecisionType,
    VerificationStatus,
)
from app.intelligence.identity_intelligence_service import (
    IdentityIntelligenceService,
)
from app.repositories.decision_record_repository import (
    DecisionRecordRepository,
)
from app.schemas.decision_record import (
    DecisionRecordAction,
    DecisionRecordCreate,
)
from app.services.audit_service import AuditService


class DecisionRecordService:
    """
    Create and retrieve authoritative organization-scoped DecisionRecords.

    Client input supplies organizational judgment only. Technical context is
    retrieved and populated by the backend.
    """

    STATUS_BY_DECISION_TYPE = {
        DecisionType.ACCEPT_RISK: DecisionStatus.ACCEPTED,
        DecisionType.CORRECT_RISK: DecisionStatus.IN_PROGRESS,
        DecisionType.ESCALATE: DecisionStatus.ESCALATED,
        DecisionType.DEFER: DecisionStatus.DEFERRED,
        DecisionType.FALSE_POSITIVE: DecisionStatus.CLOSED,
    }

    def __init__(self, db: Session):
        self.db = db
        self.repository = DecisionRecordRepository(db)
        self.audit_service = AuditService(db)
        self.intelligence_service = (
            IdentityIntelligenceService(db)
        )

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list:
        return self.repository.list_for_organization(
            organization_id
        )

    def get_by_id(
        self,
        *,
        organization_id: str,
        decision_id: str,
    ):
        return (
            self.repository
            .get_by_id_for_organization(
                organization_id=organization_id,
                decision_id=decision_id,
            )
        )

    def by_identity(
        self,
        *,
        organization_id: str,
        identity_id: str,
    ) -> list:
        return self.repository.by_identity(
            organization_id=organization_id,
            identity_id=identity_id,
        )

    def create_decision_record(
        self,
        *,
        organization_id: str,
        identity_id: str,
        recommendation_id: str,
        action: DecisionRecordAction,
    ):
        intelligence = (
            self.intelligence_service
            .get_identity_intelligence(
                identity_id
            )
        )

        if intelligence is None:
            raise ValueError(
                "Identity intelligence was not found."
            )

        recommendations = intelligence.get(
            "recommendations",
            [],
        )

        recommendation = next(
            (
                item
                for item in recommendations
                if item.get("recommendation_id")
                == recommendation_id
            ),
            None,
        )

        if recommendation is None:
            raise ValueError(
                "Recommendation was not found."
            )

        decision = intelligence.get(
            "decision",
            {},
        )

        risk = intelligence.get(
            "risk",
            {},
        )

        identity = intelligence.get(
            "identity",
            {},
        )

        status = self.STATUS_BY_DECISION_TYPE[
            action.decision_type
        ]

        payload = DecisionRecordCreate(
            organization_id=organization_id,
            identity_id=identity_id,
            decision_type=action.decision_type,
            status=status,
            title=(
                recommendation.get("title")
                or "Security decision"
            ),
            justification=action.justification,
            notes=action.notes,
            recommendation_type=(
                recommendation.get(
                    "recommendation_type"
                )
            ),
            recommendation_title=(
                recommendation.get("title")
            ),
            risk_level=(
                decision.get("priority")
                or risk.get("level")
            ),
            risk_score=risk.get("score"),
            decision_confidence=(
                decision.get(
                    "confidence",
                    {},
                ).get("score")
            ),
            evidence_snapshot_json=(
                self._build_evidence_snapshot(
                    identity=identity,
                    recommendation=recommendation,
                    decision=decision,
                )
            ),
            acceptance_type=(
                action.acceptance_type
            ),
            review_due_at=action.review_due_at,
            approval_status=(
                ApprovalStatus.NOT_REQUIRED
            ),
            action_taken=action.action_taken,
            escalated_to=action.escalated_to,
            external_ticket_reference=(
                action.external_ticket_reference
            ),
            verification_status=(
                VerificationStatus.NOT_REQUIRED
            ),
            source_system="USOP",
            source_identifier=(
                recommendation_id
            ),
            confidence_score=100,
        )

        record = self.repository.create(
            payload
        )

        self.audit_service.record(
            event_type="DecisionCreated",
            entity_type="DecisionRecord",
            entity_id=record.id,
            actor=action.actor,
            message=(
                f"{action.decision_type.value} "
                "decision recorded for "
                f"{identity.get('display_name') or identity_id}."
            ),
            metadata={
                "organization_id": organization_id,
                "identity_id": identity_id,
                "recommendation_id": (
                    recommendation_id
                ),
                "decision_type": (
                    action.decision_type.value
                ),
                "status": status.value,
                "recommendation_title": (
                    recommendation.get("title")
                ),
                "risk_level": record.risk_level,
                "actor_trust": "UserSupplied",
            },
        )

        return record

    @staticmethod
    def _build_evidence_snapshot(
        identity: dict[str, Any],
        recommendation: dict[str, Any],
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Store the minimum reusable evidence needed to explain the decision.

        Avoid raw provider payloads and credentials.
        """

        return {
            "identity": {
                "id": identity.get("id"),
                "display_name": identity.get(
                    "display_name"
                ),
                "source_system": identity.get(
                    "source_system"
                ),
            },
            "recommendation": {
                "recommendation_id": (
                    recommendation.get(
                        "recommendation_id"
                    )
                ),
                "title": recommendation.get(
                    "title"
                ),
                "description": (
                    recommendation.get(
                        "description"
                    )
                ),
                "severity": recommendation.get(
                    "severity"
                ),
                "recommendation_type": (
                    recommendation.get(
                        "recommendation_type"
                    )
                ),
                "evidence_type": (
                    recommendation.get(
                        "evidence_type"
                    )
                ),
                "role_name": recommendation.get(
                    "role_name"
                ),
                "capability": recommendation.get(
                    "capability"
                ),
                "scope_classification": (
                    recommendation.get(
                        "scope_classification"
                    )
                ),
                "assignment_classification": (
                    recommendation.get(
                        "assignment_classification"
                    )
                ),
            },
            "decision": {
                "priority": decision.get(
                    "priority"
                ),
                "summary": decision.get(
                    "summary"
                ),
                "confidence": decision.get(
                    "confidence"
                ),
                "authorization": decision.get(
                    "authorization"
                ),
                "next_step": decision.get(
                    "next_step"
                ),
            },
        }