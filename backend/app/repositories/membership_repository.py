from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.schemas.membership import MembershipCreate


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MembershipCreate) -> Membership:
        record = Membership(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[Membership]:
        return self.db.query(Membership).filter(Membership.is_active == True).all()

    def get_by_id(self, record_id: str) -> Membership | None:
        return self.db.query(Membership).filter(Membership.id == record_id).first()
