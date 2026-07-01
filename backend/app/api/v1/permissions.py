from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.permission import PermissionCreate, PermissionRead
from app.services.permission_service import PermissionService

router = APIRouter(
    prefix="/api/v1/permissions",
    tags=["Permission"],
)


@router.post("/", response_model=PermissionRead)
def create_record(data: PermissionCreate, db: Session = Depends(get_db)):
    service = PermissionService(db)
    return service.create(data)


@router.get("/", response_model=list[PermissionRead])
def list_records(db: Session = Depends(get_db)):
    service = PermissionService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=PermissionRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = PermissionService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    return record
