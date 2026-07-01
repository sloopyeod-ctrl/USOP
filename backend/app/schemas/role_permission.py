from datetime import datetime

from pydantic import BaseModel, Field


class RolePermissionCreate(BaseModel):
    role_id: str
    permission_id: str

    assignment_type: str = "Included"
    status: str = "Active"

    source_system: str | None = None
    source_identifier: str | None = None

    confidence_score: int = Field(default=100, ge=0, le=100)


class RolePermissionRead(RolePermissionCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True