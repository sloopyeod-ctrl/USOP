from sqlalchemy.orm import Session

from app.repositories.identity_attribute_repository import IdentityAttributeRepository
from app.schemas.identity_attribute import IdentityAttributeCreate


class IdentityAttributeService:
    def __init__(self, db: Session):
        self.repository = IdentityAttributeRepository(db)

    def create_attribute(self, attribute_data: IdentityAttributeCreate):
        return self.repository.create(attribute_data)

    def list_attributes(self):
        return self.repository.list_all()

    def list_attributes_by_identity(self, identity_id: str):
        return self.repository.list_by_identity(identity_id)