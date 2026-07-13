import hashlib
import json

from sqlalchemy.orm import Session

from app.domain.principal_type import PrincipalType
from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.role import Role
from app.models.role_assignment import RoleAssignment


class SnapshotBuilder:
    def __init__(self, db: Session):
        self.db = db

    def build(self, identity_id: str) -> dict:
        identity = (
            self.db.query(Identity)
            .filter(Identity.id == identity_id)
            .first()
        )

        if identity is None:
            return {}

        snapshot = {
            "identity_id": identity.id,
            "display_name": identity.display_name,
            "primary_email": identity.primary_email,
            "accounts": [],
            "groups": [],
            "roles": [],
        }

        accounts = (
            self.db.query(Account)
            .filter(
                Account.identity_id == identity.id,
                Account.is_active == True,
            )
            .all()
        )

        for account in accounts:
            snapshot["accounts"].append(
                {
                    "username": account.username,
                    "display_name": account.display_name,
                    "system_name": account.system_name,
                    "account_type": account.account_type,
                    "status": account.status,
                    "privilege_level": account.privilege_level,
                    "authentication_method": account.authentication_method,
                    "authentication_provider": account.authentication_provider,
                    "authentication_strength": account.authentication_strength,
                    "mfa_enabled": account.mfa_enabled,
                }
            )

            memberships = (
                self.db.query(Membership)
                .filter(
                    Membership.subject_type
                    == PrincipalType.ACCOUNT.value,
                    Membership.subject_id == account.id,
                    Membership.is_active.is_(True),
                )
                .all()
            )

            for membership in memberships:
                group = (
                    self.db.query(Group)
                    .filter(Group.id == membership.group_id)
                    .first()
                )

                if group:
                    snapshot["groups"].append(
                        {
                            "name": group.name,
                            "display_name": group.display_name,
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
                    .filter(Role.id == assignment.role_id)
                    .first()
                )

                if role:
                    snapshot["roles"].append(
                        {
                            "name": role.name,
                            "display_name": role.display_name,
                            "system_name": role.system_name,
                            "privilege_level": role.privilege_level,
                        }
                    )

        return snapshot

    @staticmethod
    def hash(snapshot: dict) -> str:
        payload = json.dumps(
            snapshot,
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(payload.encode()).hexdigest()