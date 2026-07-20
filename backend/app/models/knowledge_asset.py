from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.models.base import BaseSourceModel


class KnowledgeAsset(BaseSourceModel):
    """
    Organization-scoped reusable security knowledge.

    A KnowledgeAsset preserves structured organizational guidance that may
    inform many security decisions without embedding decision, identity,
    policy, evidence, approval, or authorization relationships directly
    into the asset itself.

    Relationships to other platform objects are maintained through separate
    models so the KnowledgeAsset remains reusable and independently governed.
    """

    __tablename__ = "knowledge_assets"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "title",
            "version",
            name="uq_knowledge_assets_organization_title_version",
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    guidance: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=KnowledgeAssetStatus.DRAFT.value,
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
