from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class Group(BaseSourceModel):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    group_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Security",
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