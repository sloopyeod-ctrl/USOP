from datetime import datetime

from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str
    display_name: str | None = None

    group_type: str = "Security"
    status: str = "Active"

    system_name: str
    source_system: str | None = None
    source_identifier: str | None = None

    description: str | None = None
    privilege_level: str | None = None

    confidence_score: int = Field(default=100, ge=0, le=100)


class GroupRead(GroupCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True