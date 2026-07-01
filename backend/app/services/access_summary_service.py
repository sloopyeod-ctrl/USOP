from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.role_permission import RolePermission


class AccessSummaryService:
    def __init__(self, db: Session):
        self.db = db

    def get_identity_access_summary(self, identity_id: str) -> dict | None:
        identity = self.db.query(Identity).filter(Identity.id == identity_id).first()

        if identity is None:
            return None

        accounts = self.db.query(Account).filter(Account.identity_id == identity_id).all()
        account_ids = [account.id for account in accounts]

        memberships = (
            self.db.query(Membership)
            .filter(Membership.account_id.in_(account_ids))
            .all()
            if account_ids
            else []
        )

        group_ids = [membership.group_id for membership in memberships]

        groups = (
            self.db.query(Group)
            .filter(Group.id.in_(group_ids))
            .all()
            if group_ids
            else []
        )

        role_assignments = (
            self.db.query(RoleAssignment)
            .filter(
                RoleAssignment.subject_type == "Account",
                RoleAssignment.subject_id.in_(account_ids),
            )
            .all()
            if account_ids
            else []
        )

        role_ids = [assignment.role_id for assignment in role_assignments]

        roles = (
            self.db.query(Role)
            .filter(Role.id.in_(role_ids))
            .all()
            if role_ids
            else []
        )

        role_permissions = (
            self.db.query(RolePermission)
            .filter(RolePermission.role_id.in_(role_ids))
            .all()
            if role_ids
            else []
        )

        permission_ids = [rp.permission_id for rp in role_permissions]

        permissions = (
            self.db.query(Permission)
            .filter(Permission.id.in_(permission_ids))
            .all()
            if permission_ids
            else []
        )

        return {
            "identity": {
                "id": identity.id,
                "display_name": identity.display_name,
                "identity_class": identity.identity_class,
                "status": identity.status,
                "primary_email": identity.primary_email,
            },
            "accounts": [
                {
                    "id": account.id,
                    "username": account.username,
                    "system_name": account.system_name,
                    "account_type": account.account_type,
                    "status": account.status,
                }
                for account in accounts
            ],
            "groups": [
                {
                    "id": group.id,
                    "name": group.name,
                    "display_name": group.display_name,
                    "system_name": group.system_name,
                    "privilege_level": group.privilege_level,
                }
                for group in groups
            ],
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "system_name": role.system_name,
                    "privilege_level": role.privilege_level,
                }
                for role in roles
            ],
            "permissions": [
                {
                    "id": permission.id,
                    "name": permission.name,
                    "display_name": permission.display_name,
                    "resource_type": permission.resource_type,
                    "action": permission.action,
                    "risk_level": permission.risk_level,
                }
                for permission in permissions
            ],
        }