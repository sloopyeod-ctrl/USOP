from sqlalchemy import (
    Boolean,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PlatformPermission(BaseModel):
    """
    Canonical action that may be authorized within USOP.

    Permissions form a global platform vocabulary. Organization-specific
    authority is created only when an Organization-scoped PlatformRole maps to
    a permission.

    The model is allow-oriented. Absence of a permission means the action is
    not authorized; explicit deny rules are not embedded here.
    """

    __tablename__ = "platform_permissions"

    __table_args__ = (
        UniqueConstraint(
            "resource",
            "action",
            name="uq_platform_permissions_resource_action",
        ),
    )

    permission_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    is_system_permission: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
