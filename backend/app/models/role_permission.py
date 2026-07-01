from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RolePermission(BaseModel):
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

    assignment_type: Mapped[str] = mapped_column(String(100), nullable=False, default="Included")
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="Active")

    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)

    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)