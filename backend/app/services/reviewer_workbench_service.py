from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.access_review import AccessReview
from app.models.review_campaign import ReviewCampaign


class ReviewerWorkbenchService:
    def __init__(self, db: Session):
        self.db = db

    def review_queue(self, status: str | None = None):
        query = (
            self.db.query(AccessReview)
            .filter(AccessReview.is_active == True)
        )

        if status:
            query = query.filter(AccessReview.status == status)

        reviews = (
            query.order_by(
                AccessReview.risk_score.desc(),
                AccessReview.review_due_at.asc(),
            )
            .all()
        )

        results = []

        for review in reviews:
            campaign_name = None

            if review.campaign_id:
                campaign = (
                    self.db.query(ReviewCampaign)
                    .filter(ReviewCampaign.id == review.campaign_id)
                    .first()
                )
                if campaign:
                    campaign_name = campaign.name

            results.append(
                {
                    "review_id": review.id,
                    "identity_id": review.identity_id,
                    "campaign_id": review.campaign_id,
                    "campaign_name": campaign_name,
                    "status": review.status,
                    "risk_score": review.risk_score,
                    "risk_level": review.risk_level,
                    "reason": review.reason,
                    "review_due_at": review.review_due_at,
                    "reviewed_by": review.reviewed_by,
                }
            )

        return results

    def dashboard(self):
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

        total_reviews = len(reviews)
        pending_reviews = len([r for r in reviews if r.status == "Pending"])
        needs_review = len([r for r in reviews if r.status == "Needs Review"])
        in_review = len([r for r in reviews if r.status == "In Review"])
        approved_reviews = len([r for r in reviews if r.status == "Approved"])
        rejected_reviews = len([r for r in reviews if r.status == "Rejected"])
        critical_reviews = len([r for r in reviews if r.risk_level == "Critical"])

        now = datetime.now(UTC)
        week_end = now + timedelta(days=7)
        
        overdue_reviews = len(
            [
                r
                for r in reviews
                if (
                    r.review_due_at
                    and (
                        r.review_due_at.replace(tzinfo=UTC)
                        if r.review_due_at.tzinfo is None
                        else r.review_due_at
                    )
                    < now
                    and r.status not in ("Approved", "Rejected")
                )
            ]
        )

        reviews_due_this_week = len(
            [
                r
                for r in reviews
                if (
                    r.review_due_at
                    and (
                        r.review_due_at.replace(tzinfo=UTC)
                        if r.review_due_at.tzinfo is None
                        else r.review_due_at
                    )
                    >= now
                    and (
                        r.review_due_at.replace(tzinfo=UTC)
                        if r.review_due_at.tzinfo is None
                        else r.review_due_at
                    )
                    <= week_end
                    and r.status not in ("Approved", "Rejected")
                )
            ]
        )

        return {
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "needs_review": needs_review,
            "in_review": in_review,
            "approved_reviews": approved_reviews,
            "rejected_reviews": rejected_reviews,
            "critical_reviews": critical_reviews,
            "overdue_reviews": overdue_reviews,
            "reviews_due_this_week": reviews_due_this_week,
            "active_campaigns": len(campaigns),
        }    
    
        