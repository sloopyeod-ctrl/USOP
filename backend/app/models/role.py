from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.role_type import RoleType
from app.models.base import BaseSourceModel


class Role(BaseSourceModel):
    """
    Canonical authorization role.

    role_type is stored as a string for database flexibility while its values
    are governed by the shared RoleType domain vocabulary.
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=RoleType.ACCESS.value,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )

    system_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    privilege_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )