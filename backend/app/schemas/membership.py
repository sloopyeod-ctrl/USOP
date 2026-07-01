from datetime import datetime

from pydantic import BaseModel, Field


class MembershipCreate(BaseModel):
    account_id: str
    group_id: str

    membership_type: str = "Member"
    status: str = "Active"

    source_system: str | None = None
    source_identifier: str | None = None

    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    confidence_score: int = Field(default=100, ge=0, le=100)


class MembershipRead(MembershipCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True