from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class PlatformBootstrapRequest(BaseModel):
    """
    Client-supplied identity facts for the initial Platform Administrator.

    Organization scope, actor attribution, authorization, role assignment,
    licensing, audit data, and transaction control remain server-owned.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    display_name: str = Field(
        min_length=1,
        max_length=255,
    )

    email: EmailStr

    identity_provider: str = Field(
        min_length=1,
        max_length=255,
    )

    external_tenant_id: str = Field(
        min_length=1,
        max_length=255,
    )

    external_subject_id: str = Field(
        min_length=1,
        max_length=255,
    )

    identity_issuer: str | None = Field(
        default=None,
        max_length=2048,
    )

    @field_validator(
        "display_name",
        "identity_provider",
        "external_tenant_id",
        "external_subject_id",
        "identity_issuer",
        mode="before",
    )
    @classmethod
    def normalize_string(
        cls,
        value,
    ):
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        return value.strip()


class PlatformBootstrapResult(BaseModel):
    """
    Server-produced result of atomic Platform Administrator bootstrap.

    The result exposes persisted record identifiers and lifecycle facts only.
    It does not contain credentials, tokens, secrets, seat grants, or
    browser-selected authorization values.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    organization_id: str
    license_id: str
    platform_user_id: str
    platform_role_id: str
    platform_permission_id: str
    role_permission_mapping_id: str
    role_assignment_id: str
    audit_event_ids: list[str]

    platform_user_status: str
    role_key: str
    permission_key: str

    authorization_granted: bool
    seat_allocated: bool
    authentication_completed: bool
