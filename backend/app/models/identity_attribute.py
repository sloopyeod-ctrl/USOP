from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class IdentityAttribute(BaseModel):
    __tablename__ = "identity_attributes"

    identity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=False,
        index=True,
    )

    attribute_name: Mapped[str] = mapped_column(String(100), nullable=False)
    attribute_value: Mapped[str] = mapped_column(Text, nullable=False)

    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_record: Mapped[str | None] = mapped_column(String(255), nullable=True)

    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)