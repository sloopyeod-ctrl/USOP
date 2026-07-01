from sqlalchemy.orm import Session

from app.models.role_permission import RolePermission
from app.schemas.role_permission import RolePermissionCreate


class RolePermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RolePermissionCreate) -> RolePermission:
        record = RolePermission(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[RolePermission]:
        return self.db.query(RolePermission).filter(RolePermission.is_active == True).all()

    def get_by_id(self, record_id: str) -> RolePermission | None:
        return self.db.query(RolePermission).filter(RolePermission.id == record_id).first()
