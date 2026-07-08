from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.identity_intelligence_service import IdentityIntelligenceService

router = APIRouter(
    prefix="/identity-intelligence",
    tags=["Identity Intelligence"],
)


@router.get("/{identity_id}")
def get_identity_intelligence(
    identity_id: str,
    db: Session = Depends(get_db),
):
    service = IdentityIntelligenceService(db)
    return service.get_identity_intelligence(identity_id)