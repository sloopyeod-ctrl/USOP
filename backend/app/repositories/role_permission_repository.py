from sqlalchemy.orm import Session

from app.models.role_permission import RolePermission
from app.repositories.base_repository import BaseRepository
from app.schemas.role_permission import RolePermissionCreate


class RolePermissionRepository(BaseRepository[RolePermission, RolePermissionCreate]):
    def __init__(self, db: Session):
        super().__init__(db, RolePermission)