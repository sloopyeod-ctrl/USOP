from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.subject_type import SubjectType


class RoleAssignmentCreate(BaseModel):
    """
    Request schema for a canonical subject-to-role relationship.
    """

    role_id: str

    subject_type: SubjectType = SubjectType.ACCOUNT
    subject_id: str

    assignment_type: str = "Direct"
    status: str = "Active"

    source_system: str | None = None
    source_identifier: str | None = None

    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    confidence_score: int = Field(
        default=100,
        ge=0,
        le=100,
    )


class RoleAssignmentRead(RoleAssignmentCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True