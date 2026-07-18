from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlatformUserRead(BaseModel):
    """
    Read-only representation of a USOP Platform User.

    This contract exposes Organization ownership, external identity binding,
    lifecycle state, and creation provenance only. It intentionally excludes
    credentials, passwords, access tokens, refresh tokens, commercial Seat
    state, roles, permissions, and caller-selected authority.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: str
    organization_id: str

    display_name: str
    email: str
    status: str

    identity_provider: str
    external_tenant_id: str
    external_subject_id: str
    identity_issuer: str | None

    created_via_bootstrap: bool

    invited_at: datetime | None
    activated_at: datetime | None
    last_authenticated_at: datetime | None

    created_at: datetime
    updated_at: datetime
    is_active: bool
