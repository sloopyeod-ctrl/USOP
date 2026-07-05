from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.access_review import AccessReviewCreate, AccessReviewRead
from app.services.access_review_service import AccessReviewService

router = APIRouter(
    prefix="/access-reviews",
    tags=["Access Reviews"],
)


@router.post("/", response_model=AccessReviewRead)
def create_access_review(
    data: AccessReviewCreate,
    db: Session = Depends(get_db),
):
    service = AccessReviewService(db)
    return service.create(data)


@router.get("/", response_model=list[AccessReviewRead])
def list_access_reviews(db: Session = Depends(get_db)):
    service = AccessReviewService(db)
    return service.list_all()


@router.get("/{review_id}", response_model=AccessReviewRead | None)
def get_access_review(
    review_id: str,
    db: Session = Depends(get_db),
):
    service = AccessReviewService(db)
    return service.get_by_id(review_id)