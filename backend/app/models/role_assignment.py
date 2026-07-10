from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.principal_type import PrincipalType
from app.models.base import BaseSourceModel


class RoleAssignment(BaseSourceModel):
    """
    Canonical relationship between a security principal and a role.

    subject_type and subject_id remain the persisted field names for backward
    compatibility. PrincipalType provides the canonical application vocabulary
    used to populate and validate subject_type values.

    The database stores the principal type as a string so future providers and
    principal categories do not require PostgreSQL enum migrations.
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
        default=PrincipalType.ACCOUNT.value,
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