from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlatformRoleRead(BaseModel):
    id: str
    organization_id: str
    role_key: str
    name: str
    description: str | None = None
    status: str
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
