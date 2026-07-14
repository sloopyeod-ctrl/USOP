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
    "Permission",
    "ReviewCampaign",
    "Role",
    "RoleAssignment",
    "RolePermission",
]
