from datetime import datetime

from pydantic import BaseModel, Field

from app.domain import (
    AcceptanceType,
    ApprovalStatus,
    DecisionStatus,
    DecisionType,
    VerificationStatus,
)


class DecisionRecordCreate(BaseModel):
    identity_id: str

    decision_type: DecisionType
    status: DecisionStatus = DecisionStatus.DRAFT

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    justification: str | None = None
    notes: str | None = None

    recommendation_type: str | None = None
    recommendation_title: str | None = None

    risk_level: str | None = None
    risk_score: int | None = Field(
        default=None,
        ge=0,
    )

    decision_confidence: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    evidence_snapshot_json: dict | None = None

    acceptance_type: AcceptanceType | None = None
    review_due_at: datetime | None = None

    approval_status: ApprovalStatus = (
        ApprovalStatus.NOT_REQUIRED
    )

    approved_by: str | None = None
    approved_at: datetime | None = None
    approval_notes: str | None = None

    action_taken: str | None = None

    escalated_to: str | None = None
    external_ticket_reference: str | None = None

    verification_status: VerificationStatus = (
        VerificationStatus.NOT_REQUIRED
    )

    verified_by: str | None = None
    verified_at: datetime | None = None
    verification_notes: str | None = None

    closed_by: str | None = None
    closed_at: datetime | None = None
    closure_notes: str | None = None

    source_system: str = "USOP"
    source_identifier: str | None = None

    confidence_score: int = Field(
        default=100,
        ge=0,
        le=100,
    )


class DecisionRecordRead(DecisionRecordCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class DecisionRecordAction(BaseModel):
    """
    Analyst-controlled input for recording an organizational decision.

    Risk, recommendation, identity, confidence, and evidence are populated
    by USOP from current decision intelligence.
    """

    decision_type: DecisionType

    justification: str | None = Field(
        default=None,
        max_length=10000,
    )

    notes: str | None = Field(
        default=None,
        max_length=10000,
    )

    acceptance_type: AcceptanceType | None = None
    review_due_at: datetime | None = None

    action_taken: str | None = Field(
        default=None,
        max_length=10000,
    )

    escalated_to: str | None = Field(
        default=None,
        max_length=255,
    )

    external_ticket_reference: str | None = Field(
        default=None,
        max_length=255,
    )

    actor: str | None = Field(
        default=None,
        max_length=255,
    )
