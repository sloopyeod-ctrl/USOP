from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.access_review import AccessReviewCreate, AccessReviewRead
from app.services.access_review_service import AccessReviewService
from app.analytics.access_analyzer import AccessAnalyzer
from app.governance.review_engine import ReviewEngine
from app.schemas.review_actions import ReviewAction

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

@router.post("/{review_id}/start", response_model=AccessReviewRead | None)
def start_access_review(
    review_id: str,
    action: ReviewAction,
    db: Session = Depends(get_db),
):
    service = AccessReviewService(db)
    return service.start_review(review_id, action.reviewer, action.notes)


@router.post("/{review_id}/approve", response_model=AccessReviewRead | None)
def approve_access_review(
    review_id: str,
    action: ReviewAction,
    db: Session = Depends(get_db),
):
    service = AccessReviewService(db)
    return service.approve_review(review_id, action.reviewer, action.notes)


@router.post("/{review_id}/reject", response_model=AccessReviewRead | None)
def reject_access_review(
    review_id: str,
    action: ReviewAction,
    db: Session = Depends(get_db),
):
    service = AccessReviewService(db)
    return service.reject_review(review_id, action.reviewer, action.notes)


@router.post("/{review_id}/reopen", response_model=AccessReviewRead | None)
def reopen_access_review(
    review_id: str,
    action: ReviewAction,
    db: Session = Depends(get_db),
):
    service = AccessReviewService(db)
    return service.reopen_review(review_id, action.reviewer, action.notes)