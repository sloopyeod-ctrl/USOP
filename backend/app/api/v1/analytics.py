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

@router.get("/authentication-summary")
def get_authentication_summary(db: Session = Depends(get_db)):
    analyzer = AccessAnalyzer(db)
    return analyzer.authentication_summary()

@router.get("/weak-authentication-accounts")
def list_weak_authentication_accounts(db: Session = Depends(get_db)):
    analyzer = AccessAnalyzer(db)
    return analyzer.weak_authentication_accounts()

@router.get("/identity-risk")
def list_identity_risk(db: Session = Depends(get_db)):
    analyzer = AccessAnalyzer(db)
    return analyzer.identity_risk()

