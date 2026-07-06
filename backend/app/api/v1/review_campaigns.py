from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.review_campaign import ReviewCampaignCreate, ReviewCampaignRead
from app.services.review_campaign_service import ReviewCampaignService

router = APIRouter(
    prefix="/review-campaigns",
    tags=["Review Campaigns"],
)


@router.post("/", response_model=ReviewCampaignRead)
def create_review_campaign(
    data: ReviewCampaignCreate,
    db: Session = Depends(get_db),
):
    service = ReviewCampaignService(db)
    return service.create(data)


@router.get("/", response_model=list[ReviewCampaignRead])
def list_review_campaigns(db: Session = Depends(get_db)):
    service = ReviewCampaignService(db)
    return service.list_all()


@router.get("/{campaign_id}", response_model=ReviewCampaignRead | None)
def get_review_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
):
    service = ReviewCampaignService(db)
    return service.get_by_id(campaign_id)

@router.post("/{campaign_id}/generate", response_model=ReviewCampaignRead | None)
def generate_campaign_reviews(
    campaign_id: str,
    db: Session = Depends(get_db),
):
    service = ReviewCampaignService(db)
    return service.generate_reviews(campaign_id)