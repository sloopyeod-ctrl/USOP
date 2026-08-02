from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class OrganizationalIdentity(BaseModel):
    """
    Organization-owned representation of one canonical Identity.

    OrganizationalIdentity is the tenancy anchor for operational identity
    context. It preserves organization ownership without forcing the canonical
    Identity itself to belong to only one Organization.
    """

    __tablename__ = "organizational_identities"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "identity_id",
            name=(
                "uq_organizational_identities_"
                "organization_identity"
            ),
        ),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    identity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("identities.id"),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active",
        index=True,
    )
