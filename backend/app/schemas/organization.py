from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator

from app.domain.organization_status import OrganizationStatus
from app.domain.organization_type import OrganizationType


class OrganizationCreate(BaseModel):
    """
    Request contract for creating a canonical USOP Organization.

    Commercial subscription data, governance policy, credentials, and secret
    material are intentionally excluded from this contract.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    slug: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    status: OrganizationStatus = OrganizationStatus.ACTIVE

    organization_type: OrganizationType = (
        OrganizationType.CUSTOMER
    )

    primary_domain: str | None = Field(
        default=None,
        max_length=255,
    )

    time_zone: str = Field(
        default="UTC",
        max_length=100,
    )

    description: str | None = None

    external_reference: str | None = Field(
        default=None,
        max_length=255,
    )

    deployment_identifier: str | None = Field(
        default=None,
        max_length=255,
    )

    settings_json: dict | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Organization name cannot be blank."
            )

        return normalized

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        return value.strip().lower()

    @field_validator("primary_domain")
    @classmethod
    def normalize_primary_domain(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()

        return normalized or None

    @field_validator(
        "external_reference",
        "deployment_identifier",
    )
    @classmethod
    def normalize_optional_identifier(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @field_validator("time_zone")
    @classmethod
    def validate_time_zone(cls, value: str) -> str:
        normalized = value.strip()

        try:
            ZoneInfo(normalized)
        except ZoneInfoNotFoundError as error:
            raise ValueError(
                f"Unknown IANA time zone: {normalized}"
            ) from error

        return normalized


class OrganizationRead(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    organization_type: str
    primary_domain: str | None
    time_zone: str
    description: str | None
    external_reference: str | None
    deployment_identifier: str | None
    settings_json: dict | None
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    is_active: bool

    class Config:
        from_attributes = True
