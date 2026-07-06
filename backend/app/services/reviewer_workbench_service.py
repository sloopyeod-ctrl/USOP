from sqlalchemy.orm import Session

from app.models.access_review import AccessReview
from app.models.review_campaign import ReviewCampaign


class ReviewerWorkbenchService:
    def __init__(self, db: Session):
        self.db = db

    def review_queue(self):
        reviews = (
            self.db.query(AccessReview)
            .filter(AccessReview.is_active == True)
            .order_by(
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