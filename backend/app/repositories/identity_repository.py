from sqlalchemy.orm import Session

from app.models.identity import Identity
from app.schemas.identity import IdentityCreate


class IdentityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, identity_data: IdentityCreate) -> Identity:
        identity = Identity(**identity_data.model_dump())
        self.db.add(identity)
        self.db.commit()
        self.db.refresh(identity)
        return identity

    def list(self) -> list[Identity]:
        return self.db.query(Identity).filter(Identity.is_active == True).all()

    def get_by_id(self, identity_id: str) -> Identity | None:
        return self.db.query(Identity).filter(Identity.id == identity_id).first()