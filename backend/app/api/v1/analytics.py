from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.access_analyzer import AccessAnalyzer
from app.database.session import get_db

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/privileged-identities")
def list_privileged_identities(db: Session = Depends(get_db)):
    analyzer = AccessAnalyzer(db)
    return analyzer.privileged_identities()

@router.get("/orphaned-accounts")
def list_orphaned_accounts(db: Session = Depends(get_db)):
    analyzer = AccessAnalyzer(db)
    return analyzer.orphaned_accounts()

@router.get("/dormant-accounts")
def list_dormant_accounts(
    days: int = 90,
    db: Session = Depends(get_db),
):
    analyzer = AccessAnalyzer(db)
    return analyzer.dormant_accounts(days)