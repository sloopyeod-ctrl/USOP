from sqlalchemy.orm import Session

from app.models.group import Group
from app.schemas.group import GroupCreate


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: GroupCreate) -> Group:
        record = Group(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[Group]:
        return self.db.query(Group).filter(Group.is_active == True).all()

    def get_by_id(self, record_id: str) -> Group | None:
        return self.db.query(Group).filter(Group.id == record_id).first()
