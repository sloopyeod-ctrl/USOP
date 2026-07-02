from sqlalchemy.orm import Session

from app.models.role_assignment import RoleAssignment
from app.repositories.base_repository import BaseRepository
from app.schemas.role_assignment import RoleAssignmentCreate


class RoleAssignmentRepository(BaseRepository[RoleAssignment, RoleAssignmentCreate]):
    def __init__(self, db: Session):
        super().__init__(db, RoleAssignment)