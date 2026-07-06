from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.identity_timeline_service import IdentityTimelineService

router = APIRouter(
    prefix="/identity-timeline",
    tags=["Identity Timeline"],
)


@router.get("/{identity_id}")
def get_identity_timeline(
    identity_id: str,
    db: Session = Depends(get_db),
):
    service = IdentityTimelineService(db)
    return service.get_timeline(identity_id)