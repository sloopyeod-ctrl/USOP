from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.executive_dashboard_service import ExecutiveDashboardService

router = APIRouter(
    prefix="/executive-dashboard",
    tags=["Executive Dashboard"],
)


@router.get("/")
def get_executive_dashboard(db: Session = Depends(get_db)):
    service = ExecutiveDashboardService(db)
    return service.summary()