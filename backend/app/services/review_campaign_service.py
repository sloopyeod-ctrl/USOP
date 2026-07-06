from sqlalchemy.orm import Session

from app.repositories.review_campaign_repository import ReviewCampaignRepository
from app.schemas.review_campaign import ReviewCampaignCreate


class ReviewCampaignService:
    def __init__(self, db: Session):
        self.repository = ReviewCampaignRepository(db)

    def create(self, data: ReviewCampaignCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)