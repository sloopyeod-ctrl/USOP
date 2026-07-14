from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.organization_status import OrganizationStatus
from app.domain.organization_type import OrganizationType
from app.models.base import BaseModel


class Organization(BaseModel):
    """
    Canonical customer boundary within USOP.

    An Organization represents the customer or internal operating boundary
    that owns USOP users, governance configuration, decisions, audit history,
    and commercial entitlements.

    An Organization is intentionally distinct from connected provider tenants,
    subscriptions, identity providers, and connector configurations.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=OrganizationStatus.ACTIVE.value,
        index=True,
    )

    organization_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=OrganizationType.CUSTOMER.value,
        index=True,
    )

    primary_domain: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    time_zone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="UTC",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    external_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    deployment_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    settings_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
