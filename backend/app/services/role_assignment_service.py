from sqlalchemy.orm import Session

from app.repositories.role_assignment_repository import RoleAssignmentRepository
from app.schemas.role_assignment import RoleAssignmentCreate


class RoleAssignmentService:
    def __init__(self, db: Session):
        self.repository = RoleAssignmentRepository(db)

    def create(self, data: RoleAssignmentCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
