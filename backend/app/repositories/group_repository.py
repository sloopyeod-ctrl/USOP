from sqlalchemy.orm import Session

from app.models.group import Group
from app.repositories.base_repository import BaseRepository
from app.schemas.group import GroupCreate


class GroupRepository(BaseRepository[Group, GroupCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Group)