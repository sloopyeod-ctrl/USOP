from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlatformRoleAssignmentCreate(BaseModel):
    platform_role_id: str
    expires_at: datetime | None = None


class PlatformRoleAssignmentRead(BaseModel):
    id: str
    organization_id: str
    platform_user_id: str
    platform_role_id: str
    assigned_at: datetime
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
