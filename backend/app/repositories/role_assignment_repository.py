from sqlalchemy.orm import Session

from app.models.role_assignment import RoleAssignment
from app.schemas.role_assignment import RoleAssignmentCreate


class RoleAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RoleAssignmentCreate) -> RoleAssignment:
        record = RoleAssignment(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[RoleAssignment]:
        return self.db.query(RoleAssignment).filter(RoleAssignment.is_active == True).all()

    def get_by_id(self, record_id: str) -> RoleAssignment | None:
        return self.db.query(RoleAssignment).filter(RoleAssignment.id == record_id).first()
