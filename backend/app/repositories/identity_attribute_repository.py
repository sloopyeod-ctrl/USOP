from sqlalchemy.orm import Session

from app.models.identity_attribute import IdentityAttribute
from app.repositories.base_repository import BaseRepository
from app.schemas.identity_attribute import IdentityAttributeCreate


class IdentityAttributeRepository(
    BaseRepository[IdentityAttribute, IdentityAttributeCreate]
):
    def __init__(self, db: Session):
        super().__init__(db, IdentityAttribute)

    def list_by_identity(self, identity_id: str) -> list[IdentityAttribute]:
        return (
            self.db.query(IdentityAttribute)
            .filter(
                IdentityAttribute.identity_id == identity_id,
                IdentityAttribute.is_active == True,
            )
            .all()
        )