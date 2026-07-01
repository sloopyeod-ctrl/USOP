from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: AccountCreate) -> Account:
        record = Account(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[Account]:
        return self.db.query(Account).filter(Account.is_active == True).all()

    def get_by_id(self, record_id: str) -> Account | None:
        return self.db.query(Account).filter(Account.id == record_id).first()
