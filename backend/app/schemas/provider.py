from pydantic import BaseModel, ConfigDict, Field


class ProviderDescriptorRead(BaseModel):
    """
    Read-only API representation of one registered connector provider type.

    This schema exposes immutable provider discovery metadata.

    It intentionally excludes:

    - customer configuration
    - credentials and secrets
    - runtime health
    - synchronization state
    - deployment enablement
    - licensing and entitlement decisions
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    provider_name: str = Field(
        min_length=1,
    )

    display_name: str = Field(
        min_length=1,
    )

    vendor: str = Field(
        min_length=1,
    )

    component_version: str = Field(
        min_length=1,
    )

    intelligence_domains: list[str] = Field(
        min_length=1,
    )

    capabilities: list[str] = Field(
        min_length=1,
    )

    supported_modes: list[str] = Field(
        min_length=1,
    )
