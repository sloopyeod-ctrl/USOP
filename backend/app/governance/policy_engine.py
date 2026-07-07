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

    def evaluate_condition(self, account: Account, condition: dict) -> bool:
        field = condition.get("field")
        operator = condition.get("operator", "equals")
        expected_value = condition.get("value")

        actual_value = getattr(account, field, None)

        if operator == "equals":
            return actual_value == expected_value

        if operator == "not_equals":
            return actual_value != expected_value

        if operator == "contains":
            return (
                actual_value is not None
                and expected_value is not None
                and str(expected_value).lower() in str(actual_value).lower()
            )

        if operator == "starts_with":
            return (
                actual_value is not None
                and expected_value is not None
                and str(actual_value).lower().startswith(str(expected_value).lower())
            )

        if operator == "in":
            return actual_value in expected_value if isinstance(expected_value, list) else False

        if operator == "not_in":
            return actual_value not in expected_value if isinstance(expected_value, list) else False

        return False

    def policy_matches(self, account: Account, conditions: dict) -> bool:
        if "all" in conditions:
            return all(
                self.evaluate_condition(account, condition)
                for condition in conditions["all"]
            )

        if "any" in conditions:
            return any(
                self.evaluate_condition(account, condition)
                for condition in conditions["any"]
            )

        # Backward compatibility for old simple policy format:
        # {"privilege_level": "Privileged", "mfa_enabled": false}
        for field, expected_value in conditions.items():
            actual_value = getattr(account, field, None)
            if actual_value != expected_value:
                return False

        return True

    def evaluate_account(self, account: Account) -> list[dict]:
        findings = []

        for policy in self.active_policies():
            conditions = policy.conditions_json or {}

            if self.policy_matches(account, conditions):
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