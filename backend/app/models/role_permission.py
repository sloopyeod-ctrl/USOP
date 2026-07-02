from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class RolePermission(BaseSourceModel):
    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )

    permission_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("permissions.id"),
        nullable=False,
        index=True,
    )

    assignment_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Included",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )