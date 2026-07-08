from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.timeline.identity_timeline_builder import IdentityTimelineBuilder

router = APIRouter(
    prefix="/identity-timeline-v2",
    tags=["Identity Timeline"],
)


@router.get("/{identity_id}")
def get_identity_timeline(
    identity_id: str,
    db: Session = Depends(get_db),
):
    builder = IdentityTimelineBuilder(db)
    return builder.build(identity_id)