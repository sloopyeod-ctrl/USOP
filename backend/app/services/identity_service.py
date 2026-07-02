from sqlalchemy.orm import Session

from app.repositories.identity_repository import IdentityRepository
from app.schemas.identity import IdentityCreate


class IdentityService:
    def __init__(self, db: Session):
        self.repository = IdentityRepository(db)

    def create_identity(self, identity_data: IdentityCreate):
        return self.repository.create(identity_data)

    def list_identities(self):
        return self.repository.list_all()

    def get_identity(self, identity_id: str):
        return self.repository.get_by_id(identity_id)