from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class IdentityAttribute(BaseSourceModel):
    __tablename__ = "identity_attributes"

    identity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=False,
        index=True,
    )

    attribute_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    attribute_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # This model uses source_record instead of source_identifier
    source_record: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )