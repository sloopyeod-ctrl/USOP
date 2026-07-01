from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.role_permission import RolePermissionCreate, RolePermissionRead
from app.services.role_permission_service import RolePermissionService

router = APIRouter(
    prefix="/api/v1/role-permissions",
    tags=["Role Permission"],
)


@router.post("/", response_model=RolePermissionRead)
def create_record(data: RolePermissionCreate, db: Session = Depends(get_db)):
    service = RolePermissionService(db)
    return service.create(data)


@router.get("/", response_model=list[RolePermissionRead])
def list_records(db: Session = Depends(get_db)):
    service = RolePermissionService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=RolePermissionRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = RolePermissionService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Role Permission not found")

    return record
