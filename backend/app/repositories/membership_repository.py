from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.repositories.base_repository import BaseRepository
from app.schemas.membership import MembershipCreate


class MembershipRepository(BaseRepository[Membership, MembershipCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Membership)