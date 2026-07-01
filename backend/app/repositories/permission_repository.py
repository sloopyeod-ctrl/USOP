from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: PermissionCreate) -> Permission:
        record = Permission(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[Permission]:
        return self.db.query(Permission).filter(Permission.is_active == True).all()

    def get_by_id(self, record_id: str) -> Permission | None:
        return self.db.query(Permission).filter(Permission.id == record_id).first()
