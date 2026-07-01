from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.identity import IdentityCreate, IdentityRead
from app.services.identity_service import IdentityService
from app.services.access_summary_service import AccessSummaryService

router = APIRouter(prefix="/api/v1/identities", tags=["Identities"])


@router.post("/", response_model=IdentityRead)
def create_identity(identity_data: IdentityCreate, db: Session = Depends(get_db)):
    service = IdentityService(db)
    return service.create_identity(identity_data)


@router.get("/", response_model=list[IdentityRead])
def list_identities(db: Session = Depends(get_db)):
    service = IdentityService(db)
    return service.list_identities()


@router.get("/{identity_id}", response_model=IdentityRead)
def get_identity(identity_id: str, db: Session = Depends(get_db)):
    service = IdentityService(db)
    identity = service.get_identity(identity_id)

    if identity is None:
        raise HTTPException(status_code=404, detail="Identity not found")

    return identity

@router.get("/{identity_id}/access-summary")
def get_identity_access_summary(identity_id: str, db: Session = Depends(get_db)):
    service = AccessSummaryService(db)
    summary = service.get_identity_access_summary(identity_id)

    if summary is None:
        raise HTTPException(status_code=404, detail="Identity not found")

    return summary