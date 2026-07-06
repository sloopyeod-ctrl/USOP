from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.governance.policies import (
    DEFAULT_REVIEW_INTERVAL_DAYS,
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_NEEDS_REVIEW,
    REVIEW_TYPE_RISK_TRIGGERED,
)
from app.models.access_review import AccessReview
from app.schemas.access_review import AccessReviewCreate
from app.services.access_review_service import AccessReviewService
from app.governance.snapshot_builder import SnapshotBuilder


class ReviewEngine:
    def __init__(self, db: Session):
        self.db = db
        self.review_service = AccessReviewService(db)
        self.snapshot_builder = SnapshotBuilder(db)

    def get_open_review(self, identity_id: str) -> AccessReview | None:
        return (
            self.db.query(AccessReview)
            .filter(
                AccessReview.identity_id == identity_id,
                AccessReview.is_active == True,
                AccessReview.status.in_(
                    [
                        REVIEW_STATUS_PENDING,
                        REVIEW_STATUS_NEEDS_REVIEW,
                    ]
                ),
            )
            .first()
        )

    def review_due(self, review: AccessReview | None) -> bool:
        if review is None:
            return True

        if review.review_due_at is None:
            return True

        due_at = review.review_due_at

        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=UTC)

        return due_at <= datetime.now(UTC)

    def create_review(
        self,
        identity_id: str,
        risk_score: int,
        risk_level: str,
        reason: str,
        review_type: str = REVIEW_TYPE_RISK_TRIGGERED,
    ) -> AccessReview:
        review_due_at = datetime.now(UTC) + timedelta(
            days=DEFAULT_REVIEW_INTERVAL_DAYS
        )

        snapshot = self.snapshot_builder.build(identity_id)
        snapshot_hash = self.snapshot_builder.hash(snapshot)

        review = AccessReviewCreate(
            identity_id=identity_id,
            review_type=review_type,
            status=REVIEW_STATUS_PENDING,
            risk_score=risk_score,
            risk_level=risk_level,
            reason=reason,
            review_due_at=review_due_at,
            snapshot_hash=snapshot_hash,
            snapshot_json=snapshot,
            source_system="USOP",
            source_identifier=f"review:{identity_id}",
            confidence_score=100,
        )

        return self.review_service.create(review)

    def update_open_review(
        self,
        review: AccessReview,
        risk_score: int,
        risk_level: str,
        reason: str,
    ) -> AccessReview:
        review.risk_score = risk_score
        review.risk_level = risk_level
        review.reason = reason
        review.status = REVIEW_STATUS_NEEDS_REVIEW
        review.review_due_at = datetime.now(UTC) + timedelta(
            days=DEFAULT_REVIEW_INTERVAL_DAYS
        )
        review.updated_at = datetime.now(UTC)
        snapshot = self.snapshot_builder.build(review.identity_id)
        review.snapshot_json = snapshot
        review.snapshot_hash = self.snapshot_builder.hash(snapshot)

        self.db.commit()
        self.db.refresh(review)

        return review

    def create_or_update_review(
        self,
        identity_id: str,
        risk_score: int,
        risk_level: str,
        reason: str,
    ) -> AccessReview:
        open_review = self.get_open_review(identity_id)

        if open_review:
            return self.update_open_review(
                review=open_review,
                risk_score=risk_score,
                risk_level=risk_level,
                reason=reason,
            )

        return self.create_review(
            identity_id=identity_id,
            risk_score=risk_score,
            risk_level=risk_level,
            reason=reason,
        )