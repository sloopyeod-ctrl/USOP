from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.domain.license_status import LicenseStatus
from app.models.base import BaseModel


class License(BaseModel):
    """
    Immutable commercial entitlement issued for one USOP Organization.

    A License is the persisted commercial source of truth. Runtime validation,
    expiration interpretation, grace periods, enabled capabilities, active
    seats, and effective Subscription State are derived elsewhere.

    Commercial changes must issue a new License rather than mutate the signed
    payload of an existing License.
    """

    __tablename__ = "licenses"

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    license_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=LicenseStatus.ISSUED.value,
        index=True,
    )

    commercial_edition: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=CommercialEdition.STARTER.value,
        index=True,
    )

    commercial_purpose: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=CommercialPurpose.PRODUCTION.value,
        index=True,
    )

    license_format_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    effective_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    deployment_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    seat_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    commercial_modules_json: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    feature_entitlements_json: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    canonical_payload_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    canonical_payload_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    signature: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    signing_key_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    supersedes_license_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("licenses.id"),
        nullable=True,
        index=True,
    )
