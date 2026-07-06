from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCampaignCreate(BaseModel):
    name: str
    description: str | None = None
    campaign_type: str = "Access Review"
    status: str = "Draft"
    scope: str | None = None
    owner: str | None = None

    total_reviews: int = Field(default=0, ge=0)
    completed_reviews: int = Field(default=0, ge=0)

    start_at: datetime | None = None
    due_at: datetime | None = None
    closed_at: datetime | None = None

    notes: str | None = None

    source_system: str | None = None
    source_identifier: str | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)


class ReviewCampaignRead(ReviewCampaignCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True