from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.group import GroupCreate, GroupRead
from app.services.group_service import GroupService

router = APIRouter(
    prefix="/api/v1/groups",
    tags=["Group"],
)


@router.post("/", response_model=GroupRead)
def create_record(data: GroupCreate, db: Session = Depends(get_db)):
    service = GroupService(db)
    return service.create(data)


@router.get("/", response_model=list[GroupRead])
def list_records(db: Session = Depends(get_db)):
    service = GroupService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=GroupRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = GroupService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Group not found")

    return record
