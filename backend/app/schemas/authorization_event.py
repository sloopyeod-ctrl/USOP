from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuthorizationEventCreate(BaseModel):
    organization_id: str
    organizational_identity_id: str | None = None
    identity_id: str | None = None
    account_id: str | None = None
    role_assignment_id: str | None = None

    subject_type: str
    subject_id: str
    event_type: str
    assignment_type: str | None = None

    previous_status: str | None = None
    current_status: str | None = None
    directory_scope: str | None = None
    application_scope: str | None = None

    effective_start: datetime | None = None
    effective_end: datetime | None = None
    detected_at: datetime

    risk_level: str = "Low"
    is_material: bool = False

    previous_state_json: dict | None = None
    current_state_json: dict | None = None
    evidence_json: dict | None = None

    source_system: str | None = None
    source_identifier: str | None = None
    confidence_score: int = Field(default=100, ge=0, le=100)

    @model_validator(mode="after")
    def validate_effective_window(self):
        if (
            self.effective_start is not None
            and self.effective_end is not None
            and self.effective_end < self.effective_start
        ):
            raise ValueError(
                "effective_end must not precede effective_start"
            )
        return self


class AuthorizationEventRead(AuthorizationEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool
