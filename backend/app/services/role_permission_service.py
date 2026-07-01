from sqlalchemy.orm import Session

from app.repositories.role_permission_repository import RolePermissionRepository
from app.schemas.role_permission import RolePermissionCreate


class RolePermissionService:
    def __init__(self, db: Session):
        self.repository = RolePermissionRepository(db)

    def create(self, data: RolePermissionCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
