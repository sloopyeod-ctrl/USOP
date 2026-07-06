from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.access_review import AccessReviewCreate, AccessReviewRead
from app.services.access_review_service import AccessReviewService
from app.analytics.access_analyzer import AccessAnalyzer
from app.governance.review_engine import ReviewEngine

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

@router.post("/generate-from-risk")
def generate_reviews_from_risk(db: Session = Depends(get_db)):
    analyzer = AccessAnalyzer(db)
    review_engine = ReviewEngine(db)

    generated = []

    for identity in analyzer.identity_risk():
        if identity["risk_score"] > 0:
            review = review_engine.create_or_update_review(
                identity_id=identity["identity_id"],
                risk_score=identity["risk_score"],
                risk_level=identity["risk_level"],
                reason="Automatically generated from current identity risk.",
            )

            generated.append(
                {
                    "identity_id": identity["identity_id"],
                    "review_id": review.id,
                    "risk_score": review.risk_score,
                    "risk_level": review.risk_level,
                    "status": review.status,
                }
            )

    return generated