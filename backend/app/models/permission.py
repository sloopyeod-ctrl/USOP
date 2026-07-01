from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permission_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Action",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )

    system_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)

    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(100), nullable=True)

    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)