from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.jobs.governance_jobs import GovernanceJobs

router = APIRouter(
    prefix="/governance-jobs",
    tags=["Governance Jobs"],
)


@router.post("/run-identity-risk-analysis")
def run_identity_risk_analysis(db: Session = Depends(get_db)):
    jobs = GovernanceJobs(db)
    return jobs.run_identity_risk_analysis()

@router.post("/run-connector-sync/{connector_name}")
def run_connector_sync(
    connector_name: str,
    db: Session = Depends(get_db),
):
    jobs = GovernanceJobs(db)
    return jobs.run_connector_sync(connector_name)