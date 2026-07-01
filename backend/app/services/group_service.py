from sqlalchemy.orm import Session

from app.repositories.group_repository import GroupRepository
from app.schemas.group import GroupCreate


class GroupService:
    def __init__(self, db: Session):
        self.repository = GroupRepository(db)

    def create(self, data: GroupCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
