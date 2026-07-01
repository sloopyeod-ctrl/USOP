from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Account(BaseModel):
    __tablename__ = "accounts"

    identity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    account_type: Mapped[str] = mapped_column(String(100), nullable=False, default="User")
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="Active")

    system_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)

    privilege_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    authentication_method: Mapped[str | None] = mapped_column(String(100), nullable=True)

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)