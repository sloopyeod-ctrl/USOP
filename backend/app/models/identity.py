from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Identity(BaseModel):
    __tablename__ = "identities"

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    identity_class: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Person",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )

    primary_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    primary_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    source_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    confidence_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )