from sqlalchemy import Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseSourceModel


class GovernancePolicy(BaseSourceModel):
    __tablename__ = "governance_policies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    policy_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Risk",
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Moderate",
        index=True,
    )

    risk_weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    conditions_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    actions_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )