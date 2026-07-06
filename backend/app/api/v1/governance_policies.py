from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.governance_policy import GovernancePolicyCreate, GovernancePolicyRead
from app.services.governance_policy_service import GovernancePolicyService

router = APIRouter(
    prefix="/governance-policies",
    tags=["Governance Policies"],
)


@router.post("/", response_model=GovernancePolicyRead)
def create_governance_policy(
    data: GovernancePolicyCreate,
    db: Session = Depends(get_db),
):
    service = GovernancePolicyService(db)
    return service.create(data)


@router.get("/", response_model=list[GovernancePolicyRead])
def list_governance_policies(db: Session = Depends(get_db)):
    service = GovernancePolicyService(db)
    return service.list_all()


@router.get("/{policy_id}", response_model=GovernancePolicyRead | None)
def get_governance_policy(
    policy_id: str,
    db: Session = Depends(get_db),
):
    service = GovernancePolicyService(db)
    return service.get_by_id(policy_id)