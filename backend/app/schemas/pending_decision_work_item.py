from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PendingDecisionWorkItemCreate(BaseModel):
    organization_id: str
    identity_id: str | None = None

    source_type: str
    source_id: str
    decision_category: str

    title: str
    summary: str | None = None

    priority: str = "Low"
    status: str = "Pending"
    risk_level: str = "Unknown"
    materiality_reason: str | None = None

    evidence_snapshot_json: dict = Field(default_factory=dict)

    assigned_to: str | None = None
    due_at: datetime | None = None

    source_system: str | None = None
    source_identifier: str | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)


class PendingDecisionWorkItemRead(
    PendingDecisionWorkItemCreate
):
    model_config = ConfigDict(from_attributes=True)

    id: str
    claimed_at: datetime | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    decision_record_id: str | None = None

    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool
