from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RoleCreate) -> Role:
        record = Role(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[Role]:
        return self.db.query(Role).filter(Role.is_active == True).all()

    def get_by_id(self, record_id: str) -> Role | None:
        return self.db.query(Role).filter(Role.id == record_id).first()
