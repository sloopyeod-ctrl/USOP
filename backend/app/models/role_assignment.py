from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class RoleAssignment(BaseSourceModel):
    __tablename__ = "role_assignments"

    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )

    subject_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Account",
    )

    subject_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    assignment_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Direct",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )

    first_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )