from sqlalchemy.orm import Session

from app.governance.review_engine import ReviewEngine
from app.services.audit_service import AuditService


class PolicyActionEngine:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.review_engine = ReviewEngine(db)

    def execute(self, account, findings: list[dict]):
        actions_taken = []

        for finding in findings:
            actions = finding.get("actions", {})

            if actions.get("flag_risk"):
                actions_taken.append(
                    {
                        "action": "flag_risk",
                        "username": account.username,
                    }
                )

            if actions.get("create_review"):
                review = self.review_engine.create_or_update_review(
                    identity_id=account.identity_id,
                    risk_score=finding["risk_weight"],
                    risk_level=finding["severity"],
                    reason=f"Policy violation: {finding['policy_name']}",
                )

                actions_taken.append(
                    {
                        "action": "create_review",
                        "review_id": review.id,
                    }
                )

            self.audit_service.record(
                event_type="PolicyViolation",
                entity_type="Account",
                entity_id=account.id,
                actor="USOP Policy Engine",
                message=f"Policy '{finding['policy_name']}' matched.",
                metadata={
                    "policy_id": finding["policy_id"],
                    "policy_name": finding["policy_name"],
                    "severity": finding["severity"],
                    "username": account.username,
                    "identity_id": account.identity_id,
                    "actions_taken": actions_taken,
                },
            )

        return actions_taken