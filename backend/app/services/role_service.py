from sqlalchemy.orm import Session

from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate


class RoleService:
    def __init__(self, db: Session):
        self.repository = RoleRepository(db)

    def create(self, data: RoleCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
