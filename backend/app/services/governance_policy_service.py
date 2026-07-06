from sqlalchemy.orm import Session

from app.repositories.governance_policy_repository import GovernancePolicyRepository
from app.schemas.governance_policy import GovernancePolicyCreate


class GovernancePolicyService:
    def __init__(self, db: Session):
        self.repository = GovernancePolicyRepository(db)

    def create(self, data: GovernancePolicyCreate):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)