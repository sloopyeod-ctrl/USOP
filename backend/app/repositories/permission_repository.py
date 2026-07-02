from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.repositories.base_repository import BaseRepository
from app.schemas.permission import PermissionCreate


class PermissionRepository(BaseRepository[Permission, PermissionCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Permission)