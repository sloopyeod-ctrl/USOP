from sqlalchemy.orm import Session

from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership import MembershipCreate


class MembershipService:
    def __init__(self, db: Session):
        self.repository = MembershipRepository(db)

    def create(self, data: MembershipCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
