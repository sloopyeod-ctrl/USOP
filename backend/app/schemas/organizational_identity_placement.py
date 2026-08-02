from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlacementDisposition(StrEnum):
    READY = "Ready"
    ALREADY_PLACED = "Already Placed"
    INVALID = "Invalid"
    CREATED = "Created"


class OrganizationalIdentityPlacementItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_id: str = Field(min_length=1, max_length=36)
    display_name: str | None = Field(default=None, max_length=255)
    status: str = Field(default="Active", min_length=1, max_length=100)

    @field_validator("identity_id", "status")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("The value cannot be blank.")
        return normalized

    @field_validator("display_name")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class OrganizationalIdentityPlacementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    placements: list[OrganizationalIdentityPlacementItem] = Field(
        min_length=1,
        max_length=1000,
    )


class OrganizationalIdentityPlacementResultItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_id: str
    organizational_identity_id: str | None = None
    display_name: str | None = None
    disposition: PlacementDisposition
    message: str


class OrganizationalIdentityPlacementReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: str
    dry_run: bool
    requested_count: int
    ready_count: int
    already_placed_count: int
    invalid_count: int
    created_count: int
    can_apply: bool
    results: list[OrganizationalIdentityPlacementResultItem]
