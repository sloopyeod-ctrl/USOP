from sqlalchemy.orm import Session

from app.models.identity_attribute import IdentityAttribute
from app.schemas.identity_attribute import IdentityAttributeCreate


class IdentityAttributeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, attribute_data: IdentityAttributeCreate) -> IdentityAttribute:
        attribute = IdentityAttribute(**attribute_data.model_dump())
        self.db.add(attribute)
        self.db.commit()
        self.db.refresh(attribute)
        return attribute

    def list_all(self) -> list[IdentityAttribute]:
        return (
            self.db.query(IdentityAttribute)
            .filter(IdentityAttribute.is_active == True)
            .all()
        )

    def list_by_identity(self, identity_id: str) -> list[IdentityAttribute]:
        return (
            self.db.query(IdentityAttribute)
            .filter(
                IdentityAttribute.identity_id == identity_id,
                IdentityAttribute.is_active == True,
            )
            .all()
        )