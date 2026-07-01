from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Membership(BaseModel):
    __tablename__ = "memberships"

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )

    group_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("groups.id"),
        nullable=False,
        index=True,
    )

    membership_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Member",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )

    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)

    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)