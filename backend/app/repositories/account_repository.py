from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.base_repository import BaseRepository
from app.schemas.account import AccountCreate


class AccountRepository(BaseRepository[Account, AccountCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Account)