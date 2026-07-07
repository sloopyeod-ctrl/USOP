from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.governance_policy import GovernancePolicy


class PolicyEngine:
    def __init__(self, db: Session):
        self.db = db

    def active_policies(self):
        return (
            self.db.query(GovernancePolicy)
            .filter(
                GovernancePolicy.is_active == True,
                GovernancePolicy.status == "Active",
            )
            .all()
        )

    def evaluate_account(self, account: Account) -> list[dict]:
        findings = []

        for policy in self.active_policies():
            conditions = policy.conditions_json or {}

            matches = True

            for field, expected_value in conditions.items():
                actual_value = getattr(account, field, None)

                if actual_value != expected_value:
                    matches = False
                    break

            if matches:
                findings.append(
                    {
                        "policy_id": policy.id,
                        "policy_name": policy.name,
                        "severity": policy.severity,
                        "risk_weight": policy.risk_weight,
                        "actions": policy.actions_json or {},
                        "account_id": account.id,
                        "username": account.username,
                    }
                )

        return findings