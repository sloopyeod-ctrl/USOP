from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.platform_role_status import PlatformRoleStatus
from app.models.base import BaseModel


class PlatformRole(BaseModel):
    """
    Organization-scoped authorization role for operating USOP itself.

    PlatformRole is intentionally separate from synchronized customer Role
    records. Customer roles are security objects analyzed by USOP; Platform
    roles define authority within the USOP application.

    Roles do not embed permissions. Permission mappings are maintained through
    PlatformRolePermission records.
    """

    __tablename__ = "platform_roles"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "role_key",
            name="uq_platform_roles_organization_role_key",
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    role_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=PlatformRoleStatus.ACTIVE.value,
        index=True,
    )

    is_system_role: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
