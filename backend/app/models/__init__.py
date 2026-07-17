"""
Central SQLAlchemy model registry.

Importing this package registers every mapped USOP table with the shared
SQLAlchemy metadata. Application startup, scripts, tests, and migrations
should load this registry before performing ORM operations.
"""

from app.models.access_review import AccessReview
from app.models.account import Account
from app.models.audit_event import AuditEvent
from app.models.decision_record import DecisionRecord
from app.models.governance_policy import GovernancePolicy
from app.models.group import Group
from app.models.identity import Identity
from app.models.identity_attribute import IdentityAttribute
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.license import License
from app.models.platform_permission import PlatformPermission
from app.models.platform_role import PlatformRole
from app.models.platform_role_assignment import PlatformRoleAssignment
from app.models.platform_role_permission import PlatformRolePermission
from app.models.platform_user import PlatformUser
from app.models.permission import Permission
from app.models.review_campaign import ReviewCampaign
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.role_permission import RolePermission


__all__ = [
    "AccessReview",
    "Account",
    "AuditEvent",
    "DecisionRecord",
    "GovernancePolicy",
    "Group",
    "Identity",
    "IdentityAttribute",
    "Membership",
    "Organization",
    "License",
    "PlatformPermission",
    "PlatformRole",
    "PlatformRoleAssignment",
    "PlatformRolePermission",
    "PlatformUser",
    "Permission",
    "ReviewCampaign",
    "Role",
    "RoleAssignment",
    "RolePermission",
]
