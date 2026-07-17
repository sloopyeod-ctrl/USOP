from sqlalchemy import (
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PlatformRolePermission(BaseModel):
    """
    Mapping between one PlatformRole and one PlatformPermission.

    This record grants no authority by itself. Runtime authorization must
    resolve an active Platform User, an applicable role assignment, an active
    role, and the associated permission.
    """

    __tablename__ = "platform_role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "platform_role_id",
            "platform_permission_id",
            name=(
                "uq_platform_role_permissions_"
                "role_permission"
            ),
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    platform_role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("platform_roles.id"),
        nullable=False,
        index=True,
    )

    platform_permission_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("platform_permissions.id"),
        nullable=False,
        index=True,
    )
