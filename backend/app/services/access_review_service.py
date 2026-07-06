from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.governance.policies import (
    DEFAULT_REVIEW_INTERVAL_DAYS,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_IN_REVIEW,
    REVIEW_STATUS_NEEDS_REVIEW,
    REVIEW_STATUS_REJECTED,
)
from app.repositories.access_review_repository import AccessReviewRepository
from app.schemas.access_review import AccessReviewCreate


class AccessReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AccessReviewRepository(db)

    def create(self, data: AccessReviewCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)

    def start_review(self, review_id: str, reviewer: str, notes: str | None = None):
        review = self.repository.get_by_id(review_id)
        if review is None:
            return None

        review.status = REVIEW_STATUS_IN_REVIEW
        review.reviewed_by = reviewer
        review.notes = notes
        review.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(review)
        return review

    def approve_review(self, review_id: str, reviewer: str, notes: str | None = None):
        review = self.repository.get_by_id(review_id)
        if review is None:
            return None

        now = datetime.now(UTC)

        review.status = REVIEW_STATUS_APPROVED
        review.reviewed_by = reviewer
        review.reviewed_at = now
        review.review_due_at = now + timedelta(days=DEFAULT_REVIEW_INTERVAL_DAYS)
        review.notes = notes
        review.updated_at = now

        self.db.commit()
        self.db.refresh(review)
        return review

    def reject_review(self, review_id: str, reviewer: str, notes: str | None = None):
        review = self.repository.get_by_id(review_id)
        if review is None:
            return None

        review.status = REVIEW_STATUS_REJECTED
        review.reviewed_by = reviewer
        review.reviewed_at = datetime.now(UTC)
        review.notes = notes
        review.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(review)
        return review

    def reopen_review(self, review_id: str, reviewer: str, notes: str | None = None):
        review = self.repository.get_by_id(review_id)
        if review is None:
            return None

        review.status = REVIEW_STATUS_NEEDS_REVIEW
        review.reviewed_by = reviewer
        review.notes = notes
        review.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(review)
        return review