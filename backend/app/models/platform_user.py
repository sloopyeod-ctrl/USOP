from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.platform_user_status import PlatformUserStatus
from app.models.base import BaseModel


class PlatformUser(BaseModel):
    """
    A person authorized to authenticate to and operate USOP itself.

    PlatformUser is intentionally separate from synchronized customer
    Identity and Account records. Customer identities describe the security
    environment USOP analyzes; PlatformUser describes who may operate USOP.

    Authentication credentials, passwords, access tokens, refresh tokens,
    commercial Seat state, roles, and permissions are not stored here.

    created_via_bootstrap records creation provenance only. It grants no
    permanent privilege and must never be treated as an authorization bypass.
    """

    __tablename__ = "platform_users"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "identity_provider",
            "external_tenant_id",
            "external_subject_id",
            name=(
                "uq_platform_users_organization_"
                "provider_tenant_subject"
            ),
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=PlatformUserStatus.INVITED.value,
        index=True,
    )

    identity_provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    external_tenant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    external_subject_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    identity_issuer: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    created_via_bootstrap: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    invited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_authenticated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
