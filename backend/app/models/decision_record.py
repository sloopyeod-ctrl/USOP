from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain import (
    ApprovalStatus,
    DecisionStatus,
    VerificationStatus,
)
from app.models.base import BaseSourceModel


class DecisionRecord(BaseSourceModel):
    """
    Current authoritative state of an organizational security decision.

    Historical transitions are preserved through append-only AuditEvent
    records associated with this DecisionRecord.
    """

    __tablename__ = "decision_records"

    identity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=False,
        index=True,
    )

    decision_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=DecisionStatus.DRAFT.value,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    justification: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommendation_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    recommendation_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    risk_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    decision_confidence: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    evidence_snapshot_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    acceptance_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    review_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    approval_status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=ApprovalStatus.NOT_REQUIRED.value,
        index=True,
    )

    approved_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    approval_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    action_taken: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    escalated_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    external_ticket_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=VerificationStatus.NOT_REQUIRED.value,
        index=True,
    )

    verified_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    verification_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    closed_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    closure_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
