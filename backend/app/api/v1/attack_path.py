from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.attack_path_service import AttackPathService
from app.schemas.attack_path import AttackPathResponse

router = APIRouter(
    prefix="/attack-path",
    tags=["Attack Path Intelligence"],
)


@router.get("/{identity_id}", response_model=AttackPathResponse)
def get_attack_path(identity_id: str, db: Session = Depends(get_db)):
    service = AttackPathService(db)
    result = service.get_attack_path(identity_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Identity attack path not found")

    return result