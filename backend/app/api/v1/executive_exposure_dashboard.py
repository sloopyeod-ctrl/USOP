from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.executive_exposure_dashboard_service import (
    ExecutiveExposureDashboardService,
)

router = APIRouter(
    prefix="/executive-exposure-dashboard",
    tags=["Executive Exposure Dashboard"],
)


@router.get("/")
def get_executive_exposure_dashboard(db: Session = Depends(get_db)):
    service = ExecutiveExposureDashboardService(db)
    return service.dashboard()