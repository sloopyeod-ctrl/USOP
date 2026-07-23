from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain import KnowledgeRelationshipType
from app.models.decision_knowledge import DecisionKnowledge
from app.repositories.decision_knowledge_repository import (
    DecisionKnowledgeRepository,
)
from app.repositories.decision_record_repository import (
    DecisionRecordRepository,
)
from app.repositories.knowledge_asset_repository import (
    KnowledgeAssetRepository,
)
from app.services.audit_service import AuditService


class DecisionKnowledgeServiceError(ValueError):
    """
    Base exception for DecisionKnowledge service failures.
    """


class DecisionKnowledgeDecisionNotFoundError(
    DecisionKnowledgeServiceError
):
    """
    Raised when the requested DecisionRecord is not available inside the
    requested Organization.
    """


class DecisionKnowledgeAssetNotFoundError(
    DecisionKnowledgeServiceError
):
    """
    Raised when the requested KnowledgeAsset is not available inside the
    requested Organization.
    """


class DecisionKnowledgeValidationError(
    DecisionKnowledgeServiceError
):
    """
    Raised when relationship input violates a canonical domain rule.
    """


class DecisionKnowledgeDuplicateError(
    DecisionKnowledgeServiceError
):
    """
    Raised when the canonical relationship already exists.
    """


class DecisionKnowledgeService:
    """
    Backend authority for Organization-scoped DecisionKnowledge links.

    This service validates both sides of the relationship through the same
    Organization boundary, normalizes relationship meaning, prevents
    duplicates, stages persistence, and creates a pending audit event.

    create_pending() does not commit or roll back. The caller owns the
    transaction.
    """

    def __init__(self, db: Session):
        self.db = db
        self.decision_repository = DecisionRecordRepository(db)
        self.knowledge_asset_repository = (
            KnowledgeAssetRepository(db)
        )
        self.relationship_repository = (
            DecisionKnowledgeRepository(db)
        )
        self.audit_service = AuditService(db)

    @staticmethod
    def _normalize_relationship_type(
        relationship_type: KnowledgeRelationshipType | str,
    ) -> str:
        if isinstance(
            relationship_type,
            KnowledgeRelationshipType,
        ):
            return relationship_type.value

        if not isinstance(relationship_type, str):
            raise DecisionKnowledgeValidationError(
                "DecisionKnowledge relationship type is invalid."
            )

        normalized = relationship_type.strip()

        try:
            return KnowledgeRelationshipType(
                normalized
            ).value
        except ValueError as error:
            raise DecisionKnowledgeValidationError(
                "Unknown DecisionKnowledge relationship type: "
                f"{normalized}"
            ) from error

    def _require_decision(
        self,
        *,
        organization_id: str,
        decision_record_id: str,
    ):
        decision = (
            self.decision_repository
            .get_by_id_for_organization(
                organization_id=organization_id,
                decision_id=decision_record_id,
            )
        )

        if decision is None:
            raise DecisionKnowledgeDecisionNotFoundError(
                "The DecisionKnowledge operation references a "
                "DecisionRecord that was not found in the requested "
                "Organization."
            )

        return decision

    def _require_knowledge_asset(
        self,
        *,
        organization_id: str,
        knowledge_asset_id: str,
    ):
        knowledge_asset = (
            self.knowledge_asset_repository.get_by_id(
                organization_id=organization_id,
                knowledge_asset_id=knowledge_asset_id,
            )
        )

        if knowledge_asset is None:
            raise DecisionKnowledgeAssetNotFoundError(
                "The DecisionKnowledge operation references a "
                "KnowledgeAsset that was not found in the requested "
                "Organization."
            )

        return knowledge_asset

    def create_pending(
        self,
        *,
        organization_id: str,
        decision_record_id: str,
        knowledge_asset_id: str,
        relationship_type: KnowledgeRelationshipType | str,
        actor: str | None = None,
    ) -> DecisionKnowledge:
        """
        Validate and stage one canonical DecisionKnowledge relationship.

        Both referenced records must belong to the requested Organization.
        Cross-Organization records are treated as not found so their
        existence is not disclosed.

        The caller owns commit and rollback.
        """

        decision = self._require_decision(
            organization_id=organization_id,
            decision_record_id=decision_record_id,
        )

        knowledge_asset = self._require_knowledge_asset(
            organization_id=organization_id,
            knowledge_asset_id=knowledge_asset_id,
        )

        normalized_relationship_type = (
            self._normalize_relationship_type(
                relationship_type
            )
        )

        existing_relationship = (
            self.relationship_repository.get_relationship(
                decision_record_id=decision.id,
                knowledge_asset_id=knowledge_asset.id,
                relationship_type=(
                    normalized_relationship_type
                ),
            )
        )

        if existing_relationship is not None:
            raise DecisionKnowledgeDuplicateError(
                "The DecisionRecord already has this relationship "
                "to the requested KnowledgeAsset."
            )

        relationship = DecisionKnowledge(
            decision_record_id=decision.id,
            knowledge_asset_id=knowledge_asset.id,
            relationship_type=(
                normalized_relationship_type
            ),
            created_by=actor,
            updated_by=actor,
        )

        try:
            relationship = (
                self.relationship_repository.create(
                    relationship
                )
            )

            self.audit_service.record_pending(
                event_type="DecisionKnowledgeLinked",
                entity_type="DecisionKnowledge",
                entity_id=relationship.id,
                actor=actor,
                message=(
                    "Organizational knowledge was linked to "
                    "an accountable security decision."
                ),
                metadata={
                    "organization_id": organization_id,
                    "decision_record_id": decision.id,
                    "knowledge_asset_id": knowledge_asset.id,
                    "relationship_type": (
                        relationship.relationship_type
                    ),
                    "transaction_mode": "CallerOwned",
                    "actor_trust": (
                        "CallerSupplied"
                        if actor
                        else "Unattributed"
                    ),
                },
            )

            return relationship

        except IntegrityError as error:
            raise DecisionKnowledgeDuplicateError(
                "The DecisionRecord already has this relationship "
                "to the requested KnowledgeAsset."
            ) from error

    def list_for_decision(
        self,
        *,
        organization_id: str,
        decision_record_id: str,
    ) -> list[DecisionKnowledge]:
        """
        Return active knowledge relationships for one DecisionRecord inside
        the requested Organization.
        """

        decision = self._require_decision(
            organization_id=organization_id,
            decision_record_id=decision_record_id,
        )

        return (
            self.relationship_repository.list_for_decision(
                decision.id
            )
        )
