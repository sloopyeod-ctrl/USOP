from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.role import RoleCreate, RoleRead
from app.services.role_service import RoleService

router = APIRouter(
    prefix="/api/v1/roles",
    tags=["Role"],
)


@router.post("/", response_model=RoleRead)
def create_record(data: RoleCreate, db: Session = Depends(get_db)):
    service = RoleService(db)
    return service.create(data)


@router.get("/", response_model=list[RoleRead])
def list_records(db: Session = Depends(get_db)):
    service = RoleService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=RoleRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = RoleService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return record
