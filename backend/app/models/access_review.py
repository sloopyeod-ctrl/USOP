from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class AccessReview(BaseSourceModel):
    __tablename__ = "access_reviews"

    identity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=False,
        index=True,
    )

    campaign_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("review_campaigns.id"),
        nullable=True,
        index=True,
    )

    review_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Automatic",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Pending",
        index=True,
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    risk_level: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Low",
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    review_due_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    snapshot_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    snapshot_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    