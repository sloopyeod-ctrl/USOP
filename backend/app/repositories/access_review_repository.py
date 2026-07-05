from sqlalchemy.orm import Session

from app.models.access_review import AccessReview
from app.repositories.base_repository import BaseRepository
from app.schemas.access_review import AccessReviewCreate


class AccessReviewRepository(BaseRepository[AccessReview, AccessReviewCreate]):
    def __init__(self, db: Session):
        super().__init__(db, AccessReview)