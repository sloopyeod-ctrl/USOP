from sqlalchemy import (
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain import KnowledgeRelationshipType
from app.models.base import BaseSourceModel


class DecisionKnowledge(BaseSourceModel):
    """
    Canonical relationship between an accountable security decision and
    reusable organizational knowledge.

    DecisionKnowledge preserves relationship meaning only. It does not
    duplicate KnowledgeAsset content or replace the immutable evidence
    snapshot stored by DecisionRecord.

    The referenced KnowledgeAsset row identifies the exact governed knowledge
    version associated with the decision.
    """

    __tablename__ = "decision_knowledge"

    __table_args__ = (
        UniqueConstraint(
            "decision_record_id",
            "knowledge_asset_id",
            "relationship_type",
            name=(
                "uq_decision_knowledge_"
                "decision_asset_relationship"
            ),
        ),
    )

    decision_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("decision_records.id"),
        nullable=False,
        index=True,
    )

    knowledge_asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_assets.id"),
        nullable=False,
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=KnowledgeRelationshipType.REFERENCE.value,
        index=True,
    )