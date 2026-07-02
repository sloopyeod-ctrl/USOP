from sqlalchemy.orm import Session

from app.models.identity import Identity
from app.repositories.base_repository import BaseRepository
from app.schemas.identity import IdentityCreate


class IdentityRepository(BaseRepository[Identity, IdentityCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Identity)