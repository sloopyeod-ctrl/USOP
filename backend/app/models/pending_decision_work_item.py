from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class PendingDecisionWorkItem(BaseSourceModel):
    """
    Organization-scoped work requiring human security judgment.

    This object represents unresolved analyst work. It does not represent a
    human decision and must not contain fabricated justification, acceptance,
    approval, or final disposition.
    """

    __tablename__ = "pending_decision_work_items"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "source_type",
            "source_id",
            name=(
                "uq_pending_decision_work_items_"
                "organization_source"
            ),
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    identity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=True,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    source_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    decision_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Low",
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Pending",
        index=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Unknown",
        index=True,
    )

    materiality_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_snapshot_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    resolved_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    decision_record_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("decision_records.id"),
        nullable=True,
        index=True,
    )
