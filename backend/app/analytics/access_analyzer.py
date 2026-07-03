from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from datetime import UTC, datetime, timedelta

class AccessAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def privileged_identities(self) -> list[dict]:
        identities = self.db.query(Identity).filter(Identity.is_active == True).all()
        results = []

        for identity in identities:
            accounts = (
                self.db.query(Account)
                .filter(Account.identity_id == identity.id, Account.is_active == True)
                .all()
            )

            privileged_groups = []
            privileged_roles = []

            for account in accounts:
                memberships = (
                    self.db.query(Membership)
                    .filter(
                        Membership.account_id == account.id,
                        Membership.is_active == True,
                    )
                    .all()
                )

                group_ids = [membership.group_id for membership in memberships]

                if group_ids:
                    groups = (
                        self.db.query(Group)
                        .filter(
                            Group.id.in_(group_ids),
                            Group.is_active == True,
                        )
                        .all()
                    )

                    privileged_groups.extend(
                        [
                            group
                            for group in groups
                            if group.privilege_level
                            and group.privilege_level.lower() == "privileged"
                        ]
                    )

                role_assignments = (
                    self.db.query(RoleAssignment)
                    .filter(
                        RoleAssignment.subject_type == "Account",
                        RoleAssignment.subject_id == account.id,
                        RoleAssignment.is_active == True,
                    )
                    .all()
                )

                role_ids = [assignment.role_id for assignment in role_assignments]

                if role_ids:
                    roles = (
                        self.db.query(Role)
                        .filter(
                            Role.id.in_(role_ids),
                            Role.is_active == True,
                        )
                        .all()
                    )

                    privileged_roles.extend(
                        [
                            role
                            for role in roles
                            if role.privilege_level
                            and role.privilege_level.lower()
                            in ["privileged", "admin", "administrator", "high"]
                        ]
                    )

            if privileged_groups or privileged_roles:
                results.append(
                    {
                        "identity_id": identity.id,
                        "display_name": identity.display_name,
                        "primary_email": identity.primary_email,
                        "accounts": [
                            {
                                "id": account.id,
                                "username": account.username,
                                "system_name": account.system_name,
                            }
                            for account in accounts
                        ],
                        "privileged_groups": [
                            {
                                "id": group.id,
                                "name": group.name,
                                "display_name": group.display_name,
                                "system_name": group.system_name,
                                "privilege_level": group.privilege_level,
                            }
                            for group in privileged_groups
                        ],
                        "privileged_roles": [
                            {
                                "id": role.id,
                                "name": role.name,
                                "display_name": role.display_name,
                                "system_name": role.system_name,
                                "privilege_level": role.privilege_level,
                            }
                            for role in privileged_roles
                        ],
                    }
                )

        return results
    
    def orphaned_accounts(self) -> list[dict]:
        accounts = (
            self.db.query(Account)
            .filter(
                Account.is_active == True,
                Account.identity_id == None,
            )
            .all()
        ) 

        return [
            {
                "account_id": account.id,
                "username": account.username,
                "display_name": account.display_name,
                "system_name": account.system_name,
                "account_type": account.account_type,
                "status": account.status,
                "reason": "No linked identity",
            }
            for account in accounts
        ]
    
    def dormant_accounts(self, days: int = 90) -> list[dict]:
        cutoff = datetime.now(UTC) - timedelta(days=days)

        accounts = (
            self.db.query(Account)
            .filter(Account.is_active == True)
            .all()
        )

        dormant = []

        for account in accounts:
            if account.last_seen_at is None:
                dormant.append(
                    {
                        "account_id": account.id,
                        "username": account.username,
                        "display_name": account.display_name,
                        "system_name": account.system_name,
                        "account_type": account.account_type,
                        "status": account.status,
                        "last_seen_at": None,
                        "days_inactive": None,
                        "threshold_days": days,
                        "reason": "Never seen",
                    }
                )
                continue

            last_seen = account.last_seen_at

            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=UTC)

            if last_seen < cutoff:
                dormant.append(
                    {
                        "account_id": account.id,
                        "username": account.username,
                        "display_name": account.display_name,
                        "system_name": account.system_name,
                        "account_type": account.account_type,
                        "status": account.status,
                        "last_seen_at": account.last_seen_at,
                        "days_inactive": (datetime.now(UTC) - last_seen).days,
                        "threshold_days": days,
                        "reason": f"No activity in {days}+ days",
                    }
                )

        return dormant
    
    def authentication_summary(self) -> dict:
        accounts = self.db.query(Account).filter(Account.is_active == True).all()

        summary = {
            "total_accounts": len(accounts),
            "mfa_enabled": 0,
            "mfa_disabled": 0,
            "methods": {},
            "strengths": {},
            "providers": {},
            "unknown_authentication": 0,
        }

        for account in accounts:
            if account.mfa_enabled:
                summary["mfa_enabled"] += 1
            else:
                summary["mfa_disabled"] += 1

            method = account.authentication_method or "Unknown"
            strength = account.authentication_strength or "Unknown"
            provider = account.authentication_provider or "Unknown"

            summary["methods"][method] = summary["methods"].get(method, 0) + 1
            summary["strengths"][strength] = summary["strengths"].get(strength, 0) + 1
            summary["providers"][provider] = summary["providers"].get(provider, 0) + 1

            if method == "Unknown" or strength == "Unknown" or provider == "Unknown":
                summary["unknown_authentication"] += 1

        return summary