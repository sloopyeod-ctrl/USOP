from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlatformRolePermissionCreate(BaseModel):
    platform_permission_id: str


class PlatformRolePermissionRead(BaseModel):
    id: str
    organization_id: str
    platform_role_id: str
    platform_permission_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
