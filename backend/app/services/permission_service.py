from sqlalchemy.orm import Session

from app.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionCreate


class PermissionService:
    def __init__(self, db: Session):
        self.repository = PermissionRepository(db)

    def create(self, data: PermissionCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
