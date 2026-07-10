from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.subject_type import SubjectType
from app.models.base import BaseSourceModel


class RoleAssignment(BaseSourceModel):
    """
    Canonical relationship between a subject and a role.

    subject_type identifies the canonical kind of principal represented by
    subject_id. The database stores the enum value as a string to preserve
    flexibility across providers and future subject types.
    """

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
        default=SubjectType.ACCOUNT.value,
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