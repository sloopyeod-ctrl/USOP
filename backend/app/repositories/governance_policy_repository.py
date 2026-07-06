from sqlalchemy.orm import Session

from app.models.governance_policy import GovernancePolicy
from app.repositories.base_repository import BaseRepository
from app.schemas.governance_policy import GovernancePolicyCreate


class GovernancePolicyRepository(BaseRepository[GovernancePolicy, GovernancePolicyCreate]):
    def __init__(self, db: Session):
        super().__init__(db, GovernancePolicy)