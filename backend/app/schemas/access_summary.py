from pydantic import BaseModel


class AccessSummaryIdentity(BaseModel):
    id: str
    display_name: str
    identity_class: str
    status: str
    primary_email: str | None = None


class AccessSummaryAccount(BaseModel):
    id: str
    username: str
    system_name: str
    account_type: str
    status: str


class AccessSummaryGroup(BaseModel):
    id: str
    name: str
    display_name: str | None = None
    system_name: str
    privilege_level: str | None = None


class AccessSummaryRole(BaseModel):
    id: str
    name: str
    display_name: str | None = None
    system_name: str
    privilege_level: str | None = None


class AccessSummaryPermission(BaseModel):
    id: str
    name: str
    display_name: str | None = None
    resource_type: str | None = None
    action: str | None = None
    risk_level: str | None = None


class AccessSummaryRead(BaseModel):
    identity: AccessSummaryIdentity
    accounts: list[AccessSummaryAccount]
    groups: list[AccessSummaryGroup]
    roles: list[AccessSummaryRole]
    permissions: list[AccessSummaryPermission]