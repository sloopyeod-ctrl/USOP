from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class PlatformRoleAssignment(BaseModel):
    """
    Organization-scoped assignment of one PlatformRole to one PlatformUser.

    Assignment does not authenticate the Platform User, allocate a Seat, or
    independently prove authorization. Runtime authorization must validate the
    user, role, assignment lifecycle, Organization boundary, and permission.
    """

    __tablename__ = "platform_role_assignments"

    __table_args__ = (
        UniqueConstraint(
            "platform_user_id",
            "platform_role_id",
            name=(
                "uq_platform_role_assignments_"
                "user_role"
            ),
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    platform_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("platform_users.id"),
        nullable=False,
        index=True,
    )

    platform_role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("platform_roles.id"),
        nullable=False,
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
