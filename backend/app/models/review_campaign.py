from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class ReviewCampaign(BaseSourceModel):
    __tablename__ = "review_campaigns"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Access Review",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Draft",
        index=True,
    )

    scope: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    owner: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    total_reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    start_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)