from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.membership import MembershipCreate, MembershipRead
from app.services.membership_service import MembershipService

router = APIRouter(
    prefix="/api/v1/memberships",
    tags=["Membership"],
)


@router.post("/", response_model=MembershipRead)
def create_record(data: MembershipCreate, db: Session = Depends(get_db)):
    service = MembershipService(db)
    return service.create(data)


@router.get("/", response_model=list[MembershipRead])
def list_records(db: Session = Depends(get_db)):
    service = MembershipService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=MembershipRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = MembershipService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    return record
