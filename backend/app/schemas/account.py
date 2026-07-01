from datetime import datetime

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    identity_id: str | None = None

    username: str
    display_name: str | None = None

    account_type: str = "User"
    status: str = "Active"

    system_name: str
    source_system: str | None = None
    source_identifier: str | None = None

    privilege_level: str | None = None
    authentication_method: str | None = None

    last_seen_at: datetime | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)


class AccountRead(AccountCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True