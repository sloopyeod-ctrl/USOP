from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class AuthorizationEvent(BaseSourceModel):
    """
    Append-only historical evidence of an authorization-state change.

    AuthorizationEvent records facts. It does not own analyst decisions,
    approvals, verification, closure, or ticketing workflows.
    """

    __tablename__ = "authorization_events"

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    organizational_identity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("organizational_identities.id"),
        nullable=True,
        index=True,
    )

    identity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=True,
        index=True,
    )

    account_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("accounts.id"),
        nullable=True,
        index=True,
    )

    role_assignment_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("role_assignments.id"),
        nullable=True,
        index=True,
    )

    subject_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    assignment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    current_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    directory_scope: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        index=True,
    )

    application_scope: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        index=True,
    )

    effective_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    effective_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Low",
        index=True,
    )

    is_material: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    previous_state_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    current_state_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    evidence_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
