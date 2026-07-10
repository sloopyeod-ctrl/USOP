from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.principal_type import PrincipalType


class MembershipCreate(BaseModel):
    """
    Request schema for a canonical principal-to-group relationship.
    """

    subject_type: PrincipalType = PrincipalType.ACCOUNT
    subject_id: str
    group_id: str

    membership_type: str = "Member"
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


class MembershipRead(MembershipCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True