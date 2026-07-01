from sqlalchemy.orm import Session

from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate


class AccountService:
    def __init__(self, db: Session):
        self.repository = AccountRepository(db)

    def create(self, data: AccountCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
