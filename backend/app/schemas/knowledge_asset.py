from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)


class KnowledgeAssetCreate(BaseModel):
    """
    Request contract for creating Organization-scoped Organizational Memory.

    The Organization boundary is supplied by the API path. Version allocation,
    record identity, timestamps, lifecycle provenance, transaction management,
    and audit attribution remain server-controlled.

    Actor identity is intentionally excluded so callers cannot select their
    own audit authority.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    guidance: str = Field(
        min_length=1,
    )

    category: KnowledgeCategory

    status: KnowledgeAssetStatus = (
        KnowledgeAssetStatus.DRAFT
    )

    summary: str | None = None

    source_system: str | None = Field(
        default=None,
        max_length=100,
    )

    source_identifier: str | None = Field(
        default=None,
        max_length=255,
    )

    confidence_score: int = Field(
        default=100,
        ge=0,
        le=100,
    )


class KnowledgeAssetRead(BaseModel):
    """
    Read representation of one reusable Organizational Memory asset.

    This contract exposes the canonical asset, lifecycle state, source
    provenance, version, and shared record metadata. Audit events,
    transaction state, and future relationship objects are intentionally
    excluded from the asset representation.
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
