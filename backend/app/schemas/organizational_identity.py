from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrganizationalIdentityCreate(BaseModel):
    """
    Caller-supplied contract for placing one canonical Identity into an
    Organization.

    Organization ownership is supplied by the service boundary rather than the
    request payload.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    identity_id: str = Field(
        min_length=1,
        max_length=36,
    )

    display_name: str | None = Field(
        default=None,
        max_length=255,
    )

    status: str = Field(
        default="Active",
        min_length=1,
        max_length=100,
    )

    @field_validator(
        "identity_id",
        "status",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "The value cannot be blank."
            )

        return normalized

    @field_validator("display_name")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class OrganizationalIdentityRead(BaseModel):
    """
    Read contract for one Organization-owned identity placement.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: str
    organization_id: str
    identity_id: str
    display_name: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    is_active: bool
