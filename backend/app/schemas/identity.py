from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class IdentityCreate(BaseModel):
    display_name: str
    identity_class: str = "Person"
    status: str = "Active"

    primary_email: EmailStr | None = None
    primary_phone: str | None = None

    source_system: str | None = None
    source_identifier: str | None = None

    confidence_score: int = Field(default=100, ge=0, le=100)


class IdentityRead(IdentityCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True