from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.role_assignment import RoleAssignmentCreate, RoleAssignmentRead
from app.services.role_assignment_service import RoleAssignmentService

router = APIRouter(
    prefix="/api/v1/role-assignments",
    tags=["Role Assignment"],
)


@router.post("/", response_model=RoleAssignmentRead)
def create_record(data: RoleAssignmentCreate, db: Session = Depends(get_db)):
    service = RoleAssignmentService(db)
    return service.create(data)


@router.get("/", response_model=list[RoleAssignmentRead])
def list_records(db: Session = Depends(get_db)):
    service = RoleAssignmentService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=RoleAssignmentRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = RoleAssignmentService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Role Assignment not found")

    return record
