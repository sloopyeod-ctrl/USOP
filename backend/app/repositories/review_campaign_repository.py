from sqlalchemy.orm import Session

from app.models.review_campaign import ReviewCampaign
from app.repositories.base_repository import BaseRepository
from app.schemas.review_campaign import ReviewCampaignCreate


class ReviewCampaignRepository(BaseRepository[ReviewCampaign, ReviewCampaignCreate]):
    def __init__(self, db: Session):
        super().__init__(db, ReviewCampaign)