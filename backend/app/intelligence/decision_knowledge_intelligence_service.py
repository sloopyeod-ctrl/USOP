from sqlalchemy.orm import Session

from app.repositories.knowledge_asset_repository import (
    KnowledgeAssetRepository,
)
from app.services.decision_knowledge_service import (
    DecisionKnowledgeService,
)


class DecisionKnowledgeIntelligenceError(RuntimeError):
    """
    Base exception for DecisionKnowledge intelligence failures.
    """


class DecisionKnowledgeIntelligenceIntegrityError(
    DecisionKnowledgeIntelligenceError
):
    """
    Raised when a canonical relationship cannot be resolved to a governed
    KnowledgeAsset within the DecisionRecord's Organization.
    """


class DecisionKnowledgeIntelligenceService:
    """
    Assemble analyst-ready Organizational Memory for security decisions.

    Persistence and transaction responsibilities remain in repositories and
    domain services. This intelligence service performs read-only
    orchestration and projection.

    KnowledgeAssets are loaded in one organization-scoped bulk query to avoid
    an N+1 lookup pattern.
    """

    def __init__(self, db: Session):
        self.db = db
        self.relationship_service = (
            DecisionKnowledgeService(db)
        )
        self.knowledge_asset_repository = (
            KnowledgeAssetRepository(db)
        )

    def list_for_decision(
        self,
        *,
        organization_id: str,
        decision_record_id: str,
    ) -> list[dict]:
        """
        Return relationship meaning and complete governed knowledge for one
        DecisionRecord inside the requested Organization.
        """

        relationships = (
            self.relationship_service.list_for_decision(
                organization_id=organization_id,
                decision_record_id=decision_record_id,
            )
        )

        if not relationships:
            return []

        knowledge_asset_ids = list(
            dict.fromkeys(
                relationship.knowledge_asset_id
                for relationship in relationships
            )
        )

        knowledge_assets = (
            self.knowledge_asset_repository.list_by_ids(
                organization_id=organization_id,
                knowledge_asset_ids=knowledge_asset_ids,
            )
        )

        knowledge_by_id = {
            knowledge_asset.id: knowledge_asset
            for knowledge_asset in knowledge_assets
        }

        projections: list[dict] = []

        for relationship in relationships:
            knowledge_asset = knowledge_by_id.get(
                relationship.knowledge_asset_id
            )

            if knowledge_asset is None:
                raise (
                    DecisionKnowledgeIntelligenceIntegrityError(
                        "DecisionKnowledge relationship could not be "
                        "resolved to a KnowledgeAsset within the "
                        "requested Organization."
                    )
                )

            projections.append(
                {
                    "relationship": {
                        "id": relationship.id,
                        "decision_record_id": (
                            relationship.decision_record_id
                        ),
                        "relationship_type": (
                            relationship.relationship_type
                        ),
                        "created_at": (
                            relationship.created_at
                        ),
                        "updated_at": (
                            relationship.updated_at
                        ),
                        "created_by": (
                            relationship.created_by
                        ),
                        "updated_by": (
                            relationship.updated_by
                        ),
                        "is_active": (
                            relationship.is_active
                        ),
                    },
                    "knowledge": {
                        "id": knowledge_asset.id,
                        "organization_id": (
                            knowledge_asset.organization_id
                        ),
                        "title": knowledge_asset.title,
                        "summary": knowledge_asset.summary,
                        "guidance": knowledge_asset.guidance,
                        "category": knowledge_asset.category,
                        "status": knowledge_asset.status,
                        "version": knowledge_asset.version,
                        "source_system": (
                            knowledge_asset.source_system
                        ),
                        "source_identifier": (
                            knowledge_asset.source_identifier
                        ),
                        "confidence_score": (
                            knowledge_asset.confidence_score
                        ),
                        "created_at": (
                            knowledge_asset.created_at
                        ),
                        "updated_at": (
                            knowledge_asset.updated_at
                        ),
                        "created_by": (
                            knowledge_asset.created_by
                        ),
                        "updated_by": (
                            knowledge_asset.updated_by
                        ),
                        "is_active": (
                            knowledge_asset.is_active
                        ),
                    },
                }
            )

        return projections
