from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class AuditEvent(BaseSourceModel):
    __tablename__ = "audit_events"

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    actor: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )