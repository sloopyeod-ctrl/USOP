from sqlalchemy.orm import Session

from app.repositories.access_review_repository import AccessReviewRepository
from app.schemas.access_review import AccessReviewCreate


class AccessReviewService:
    def __init__(self, db: Session):
        self.repository = AccessReviewRepository(db)

    def create(self, data: AccessReviewCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)