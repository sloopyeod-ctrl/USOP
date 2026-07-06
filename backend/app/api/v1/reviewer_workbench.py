from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.reviewer_workbench_service import ReviewerWorkbenchService

router = APIRouter(
    prefix="/reviewer-workbench",
    tags=["Reviewer Workbench"],
)


@router.get("/")
def get_review_queue(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    service = ReviewerWorkbenchService(db)
    return service.review_queue(status)