from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.account import AccountCreate, AccountRead
from app.services.account_service import AccountService

router = APIRouter(
    prefix="/api/v1/accounts",
    tags=["Account"],
)


@router.post("/", response_model=AccountRead)
def create_record(data: AccountCreate, db: Session = Depends(get_db)):
    service = AccountService(db)
    return service.create(data)


@router.get("/", response_model=list[AccountRead])
def list_records(db: Session = Depends(get_db)):
    service = AccountService(db)
    return service.list_all()


@router.get("/{record_id}", response_model=AccountRead)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = AccountService(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return record
