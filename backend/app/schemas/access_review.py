from datetime import datetime

from pydantic import BaseModel, Field


class AccessReviewCreate(BaseModel):
    identity_id: str
    review_type: str = "Automatic"
    status: str = "Pending"

    risk_score: int = Field(default=0, ge=0)
    risk_level: str = "Low"

    reason: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    review_due_at: datetime | None = None
    snapshot_hash: str | None = None
    snapshot_json: dict | None = None
    notes: str | None = None

    source_system: str | None = None
    source_identifier: str | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)


class AccessReviewRead(AccessReviewCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True