from pydantic import BaseModel, ConfigDict


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
