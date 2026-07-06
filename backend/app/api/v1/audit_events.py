from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/audit-events",
    tags=["Audit Events"],
)


@router.get("/")
def list_audit_events(db: Session = Depends(get_db)):
    service = AuditService(db)
    return service.repository.list_all()


@router.get("/{entity_type}/{entity_id}")
def list_audit_events_by_entity(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
):
    service = AuditService(db)
    return service.repository.by_entity(entity_type, entity_id)