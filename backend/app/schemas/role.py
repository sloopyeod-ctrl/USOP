from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.role_type import RoleType


class RoleCreate(BaseModel):
    """
    Request schema for a canonical authorization role.
    """

    name: str
    display_name: str | None = None

    role_type: RoleType = RoleType.ACCESS
    status: str = "Active"

    system_name: str
    source_system: str | None = None
    source_identifier: str | None = None

    description: str | None = None
    privilege_level: str | None = None

    confidence_score: int = Field(
        default=100,
        ge=0,
        le=100,
    )


class RoleRead(RoleCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True