from datetime import datetime
from pydantic import BaseModel, EmailStr


class IdentityCreate(BaseModel):
    display_name: str
    identity_type: str = "Unknown"
    identity_status: str = "Active"

    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    department: str | None = None
    organization: str | None = None
    manager_identity_id: str | None = None
    employee_id: str | None = None
    source_system: str | None = None
    source_identifier: str | None = None
    notes: str | None = None


class IdentityRead(IdentityCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True