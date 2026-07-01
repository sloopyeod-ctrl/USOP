from datetime import datetime

from pydantic import BaseModel, Field


class IdentityAttributeCreate(BaseModel):
    identity_id: str
    attribute_name: str
    attribute_value: str
    source_system: str | None = None
    source_record: str | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)
    verified_at: datetime | None = None


class IdentityAttributeRead(IdentityAttributeCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True