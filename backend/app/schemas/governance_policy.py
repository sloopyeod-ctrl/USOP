from datetime import datetime

from pydantic import BaseModel, Field


class GovernancePolicyCreate(BaseModel):
    name: str
    description: str | None = None
    policy_type: str = "Risk"
    status: str = "Active"
    severity: str = "Moderate"
    risk_weight: int = Field(default=0, ge=0)
    conditions_json: dict | None = None
    actions_json: dict | None = None

    source_system: str | None = None
    source_identifier: str | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)


class GovernancePolicyRead(GovernancePolicyCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True