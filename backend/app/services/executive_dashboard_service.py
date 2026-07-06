from sqlalchemy.orm import Session

from app.models.access_review import AccessReview
from app.models.account import Account
from app.models.audit_event import AuditEvent
from app.models.identity import Identity
from app.models.review_campaign import ReviewCampaign


class ExecutiveDashboardService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self):
        identities = (
            self.db.query(Identity)
            .filter(Identity.is_active == True)
            .all()
        )

        accounts = (
            self.db.query(Account)
            .filter(Account.is_active == True)
            .all()
        )

        reviews = (
            self.db.query(AccessReview)
            .filter(AccessReview.is_active == True)
            .all()
        )

        campaigns = (
            self.db.query(ReviewCampaign)
            .filter(ReviewCampaign.is_active == True)
            .all()
        )

        audit_events = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.is_active == True)
            .all()
        )

        return {
            "total_identities": len(identities),
            "total_accounts": len(accounts),
            "total_reviews": len(reviews),
            "pending_reviews": len([r for r in reviews if r.status == "Pending"]),
            "needs_review": len([r for r in reviews if r.status == "Needs Review"]),
            "approved_reviews": len([r for r in reviews if r.status == "Approved"]),
            "rejected_reviews": len([r for r in reviews if r.status == "Rejected"]),
            "critical_reviews": len([r for r in reviews if r.risk_level == "Critical"]),
            "active_campaigns": len(campaigns),
            "total_audit_events": len(audit_events),
            "privileged_accounts": len(
                [
                    a for a in accounts
                    if a.privilege_level
                    and a.privilege_level.lower() in ["privileged", "admin", "administrator", "high"]
                ]
            ),
            "mfa_disabled_accounts": len([a for a in accounts if a.mfa_enabled is False]),
        }