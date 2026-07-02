from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.base_repository import BaseRepository
from app.schemas.role import RoleCreate


class RoleRepository(BaseRepository[Role, RoleCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Role)