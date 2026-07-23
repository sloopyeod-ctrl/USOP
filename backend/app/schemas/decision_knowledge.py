from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain import KnowledgeRelationshipType


class DecisionKnowledgeCreate(BaseModel):
    """
    Request contract for linking Organizational Memory to a DecisionRecord.

    Organization ownership and DecisionRecord identity are supplied by the
    API path. Record identity, timestamps, actor attribution, and transaction
    management remain server-controlled.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    knowledge_asset_id: str
    relationship_type: KnowledgeRelationshipType = (
        KnowledgeRelationshipType.REFERENCE
    )


class DecisionKnowledgeRead(BaseModel):
    """
    Read representation of one canonical DecisionKnowledge relationship.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: str
    decision_record_id: str
    knowledge_asset_id: str
    relationship_type: str

    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    is_active: bool


class DecisionKnowledgeRelationshipRead(BaseModel):
    """
    Relationship context included in analyst-ready knowledge intelligence.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: str
    decision_record_id: str
    relationship_type: str

    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    is_active: bool


class DecisionKnowledgeAssetRead(BaseModel):
    """
    Governed KnowledgeAsset content exposed inside decision intelligence.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: str
    organization_id: str

    title: str
    summary: str | None
    guidance: str

    category: str
    status: str
    version: int

    source_system: str | None
    source_identifier: str | None
    confidence_score: int

    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    is_active: bool


class DecisionKnowledgeIntelligenceRead(BaseModel):
    """
    Analyst-ready projection joining relationship meaning with the exact
    governed KnowledgeAsset version used by a DecisionRecord.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    relationship: DecisionKnowledgeRelationshipRead
    knowledge: DecisionKnowledgeAssetRead
