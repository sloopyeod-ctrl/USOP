from sqlalchemy.orm import Session

from app.domain.principal_type import PrincipalType
from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from datetime import UTC, datetime, timedelta
from app.analytics.risk_engine import RISK_WEIGHTS, risk_level
from app.governance.policy_engine import PolicyEngine
from app.governance.policy_action_engine import PolicyActionEngine

class AccessAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.policy_engine = PolicyEngine(db)
        self.policy_action_engine = PolicyActionEngine(db)

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
                        Membership.subject_type
                        == PrincipalType.ACCOUNT.value,
                        Membership.subject_id == account.id,
                        Membership.is_active.is_(True),
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
    
    def weak_authentication_accounts(self) -> list[dict]:
        accounts = self.db.query(Account).filter(Account.is_active == True).all()
        results = []

        for account in accounts:
            findings = []

            method = account.authentication_method
            strength = account.authentication_strength
            provider = account.authentication_provider

            if account.mfa_enabled is False:
                findings.append("MFA Disabled")

            if not method:
                findings.append("Authentication Method Unknown")

            if not strength:
                findings.append("Authentication Strength Unknown")
            elif strength.lower() == "weak":
                findings.append("Weak Authentication Strength")

            if not provider:
                findings.append("Authentication Provider Unknown")

            if findings:
                results.append(
                    {
                        "account_id": account.id,
                        "username": account.username,
                        "display_name": account.display_name,
                        "system_name": account.system_name,
                        "account_type": account.account_type,
                        "status": account.status,
                        "privilege_level": account.privilege_level,
                        "authentication_method": method,
                        "authentication_strength": strength,
                        "authentication_provider": provider,
                        "mfa_enabled": account.mfa_enabled,
                        "findings": findings,
                    }
                )

        return results
    
    def identity_risk(self) -> list[dict]:
        identities = self.db.query(Identity).filter(Identity.is_active == True).all()
        results = []

        weak_auth_accounts = self.weak_authentication_accounts()
        weak_auth_account_ids = {
            account["account_id"] for account in weak_auth_accounts
        }

        dormant_accounts = self.dormant_accounts()
        dormant_account_ids = {
            account["account_id"] for account in dormant_accounts
        }

        for identity in identities:
            score = 0
            findings = []

            accounts = (
                self.db.query(Account)
                .filter(Account.identity_id == identity.id, Account.is_active == True)
                .all()
            )

            for account in accounts:
                if account.id in weak_auth_account_ids:
                    score += RISK_WEIGHTS["weak_authentication"]
                    findings.append(
                        {
                            "type": "weak_authentication",
                            "weight": RISK_WEIGHTS["weak_authentication"],
                            "account_id": account.id,
                            "username": account.username,
                        }
                    )

                if account.id in dormant_account_ids:
                    score += RISK_WEIGHTS["dormant_account"]
                    findings.append(
                        {
                            "type": "dormant_account",
                            "weight": RISK_WEIGHTS["dormant_account"],
                            "account_id": account.id,
                            "username": account.username,
                        }
                    )

                policy_findings = self.policy_engine.evaluate_account(account)

                self.policy_action_engine.execute(
                    account,
                    policy_findings,
                )

                for policy_finding in policy_findings:
                    score += policy_finding["risk_weight"]
                    findings.append(
                        {
                            "type": "policy_violation",
                            "weight": policy_finding["risk_weight"],
                            "policy_id": policy_finding["policy_id"],
                            "policy_name": policy_finding["policy_name"],
                            "severity": policy_finding["severity"],
                            "account_id": policy_finding["account_id"],
                            "username": policy_finding["username"],
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

                group_ids = [membership.group_id for membership in memberships]

                if group_ids:
                    groups = (
                        self.db.query(Group)
                        .filter(Group.id.in_(group_ids), Group.is_active == True)
                        .all()
                    )

                    for group in groups:
                        if group.privilege_level and group.privilege_level.lower() == "privileged":
                            score += RISK_WEIGHTS["privileged_group"]
                            findings.append(
                                {
                                    "type": "privileged_group",
                                    "weight": RISK_WEIGHTS["privileged_group"],
                                    "group_id": group.id,
                                    "group_name": group.name,
                                }
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
                        .filter(Role.id.in_(role_ids), Role.is_active == True)
                        .all()
                    )

                    for role in roles:
                        if role.privilege_level and role.privilege_level.lower() in [
                            "privileged",
                            "admin",
                            "administrator",
                            "high",
                        ]:
                            score += RISK_WEIGHTS["privileged_role"]
                            findings.append(
                                {
                                    "type": "privileged_role",
                                    "weight": RISK_WEIGHTS["privileged_role"],
                                    "role_id": role.id,
                                    "role_name": role.name,
                                }
                            )

            results.append(
                {
                    "identity_id": identity.id,
                    "display_name": identity.display_name,
                    "primary_email": identity.primary_email,
                    "risk_score": score,
                    "risk_level": risk_level(score),
                    "findings": findings,
                }
            )

        return results