from datetime import datetime

from pydantic import BaseModel, Field


class PermissionCreate(BaseModel):
    name: str
    display_name: str | None = None

    permission_type: str = "Action"
    status: str = "Active"

    system_name: str
    source_system: str | None = None
    source_identifier: str | None = None

    resource_type: str | None = None
    action: str | None = None

    description: str | None = None
    risk_level: str | None = None

    confidence_score: int = Field(default=100, ge=0, le=100)


class PermissionRead(PermissionCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True