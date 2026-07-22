from sqlalchemy.orm import Session

from app.models.decision_knowledge import DecisionKnowledge


class DecisionKnowledgeRepository:
    """
    Persistence boundary for canonical DecisionKnowledge relationships.

    This repository stores and retrieves relationships but performs no
    validation, authorization, tenancy verification, audit creation,
    relationship interpretation, or transaction management.

    The calling service owns commit and rollback.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        relationship: DecisionKnowledge,
    ) -> DecisionKnowledge:
        """
        Stage one DecisionKnowledge relationship inside the caller's
        transaction.
        """

        self.db.add(relationship)
        self.db.flush()
        self.db.refresh(relationship)

        return relationship

    def get_relationship(
        self,
        *,
        decision_record_id: str,
        knowledge_asset_id: str,
        relationship_type: str,
    ) -> DecisionKnowledge | None:
        """
        Return one canonical DecisionKnowledge relationship if it exists.
        """

        return (
            self.db.query(DecisionKnowledge)
            .filter(
                DecisionKnowledge.decision_record_id
                == decision_record_id,
                DecisionKnowledge.knowledge_asset_id
                == knowledge_asset_id,
                DecisionKnowledge.relationship_type
                == relationship_type,
            )
            .one_or_none()
        )    

    def list_for_decision(
        self,
        decision_record_id: str,
    ) -> list[DecisionKnowledge]:
        """
        Return all active Knowledge relationships for one Decision.
        """

        return (
            self.db.query(DecisionKnowledge)
            .filter(
                DecisionKnowledge.decision_record_id
                == decision_record_id,
                DecisionKnowledge.is_active.is_(True),
            )
            .order_by(
                DecisionKnowledge.created_at.asc(),
                DecisionKnowledge.id.asc(),
            )
            .all()
        )

    def list_for_knowledge_asset(
        self,
        knowledge_asset_id: str,
    ) -> list[DecisionKnowledge]:
        """
        Return every active Decision referencing one KnowledgeAsset.
        """

        return (
            self.db.query(DecisionKnowledge)
            .filter(
                DecisionKnowledge.knowledge_asset_id
                == knowledge_asset_id,
                DecisionKnowledge.is_active.is_(True),
            )
            .order_by(
                DecisionKnowledge.created_at.asc(),
                DecisionKnowledge.id.asc(),
            )
            .all()
        )