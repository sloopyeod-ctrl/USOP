from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.role import Role
from app.models.role_assignment import RoleAssignment


class IdentityGraphService:
    def __init__(self, db: Session):
        self.db = db

    def get_identity_graph(self, identity_id: str):
        identity = (
            self.db.query(Identity)
            .filter(
                Identity.id == identity_id,
                Identity.is_active == True,
            )
            .first()
        )

        if identity is None:
            return None

        accounts = (
            self.db.query(Account)
            .filter(
                Account.identity_id == identity.id,
                Account.is_active == True,
            )
            .all()
        )

        account_results = []
        group_results = []
        role_results = []

        for account in accounts:
            account_results.append(
                {
                    "id": account.id,
                    "username": account.username,
                    "display_name": account.display_name,
                    "system_name": account.system_name,
                    "account_type": account.account_type,
                    "status": account.status,
                    "privilege_level": account.privilege_level,
                    "mfa_enabled": account.mfa_enabled,
                }
            )

            memberships = (
                self.db.query(Membership)
                .filter(
                    Membership.account_id == account.id,
                    Membership.is_active == True,
                )
                .all()
            )

            for membership in memberships:
                group = (
                    self.db.query(Group)
                    .filter(
                        Group.id == membership.group_id,
                        Group.is_active == True,
                    )
                    .first()
                )

                if group:
                    group_results.append(
                        {
                            "account_id": account.id,
                            "username": account.username,
                            "group_id": group.id,
                            "group_name": group.name,
                            "system_name": group.system_name,
                            "privilege_level": group.privilege_level,
                        }
                    )

            assignments = (
                self.db.query(RoleAssignment)
                .filter(
                    RoleAssignment.subject_type == "Account",
                    RoleAssignment.subject_id == account.id,
                    RoleAssignment.is_active == True,
                )
                .all()
            )

            for assignment in assignments:
                role = (
                    self.db.query(Role)
                    .filter(
                        Role.id == assignment.role_id,
                        Role.is_active == True,
                    )
                    .first()
                )

                if role:
                    role_results.append(
                        {
                            "account_id": account.id,
                            "username": account.username,
                            "role_id": role.id,
                            "role_name": role.name,
                            "system_name": role.system_name,
                            "privilege_level": role.privilege_level,
                        }
                    )

        return {
            "identity": {
                "id": identity.id,
                "display_name": identity.display_name,
                "primary_email": identity.primary_email,
            },
            "accounts": account_results,
            "groups": group_results,
            "roles": role_results,
        }