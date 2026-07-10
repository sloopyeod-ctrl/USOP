from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.principal_type import PrincipalType
from app.models.base import BaseSourceModel


class Membership(BaseSourceModel):
    """
    Canonical relationship between a security principal and a group.

    subject_type identifies the canonical kind of principal represented by
    subject_id. The value is governed by the PrincipalType domain vocabulary.

    subject_id intentionally does not use a database foreign key because it
    may reference different canonical tables depending on subject_type.

    Examples:

    - Account -> Group
    - ServicePrincipal -> Group
    - Device -> Group
    - Group -> Group
    - Workload -> Group
    """

    __tablename__ = "memberships"

    subject_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=PrincipalType.ACCOUNT.value,
        index=True,
    )

    subject_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    group_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("groups.id"),
        nullable=False,
        index=True,
    )

    membership_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Member",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
    )

    first_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )