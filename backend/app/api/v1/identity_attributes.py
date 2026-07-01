from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.identity_attribute import (
    IdentityAttributeCreate,
    IdentityAttributeRead,
)
from app.services.identity_attribute_service import IdentityAttributeService

router = APIRouter(
    prefix="/api/v1/identity-attributes",
    tags=["Identity Attributes"],
)


@router.post("/", response_model=IdentityAttributeRead)
def create_identity_attribute(
    attribute_data: IdentityAttributeCreate,
    db: Session = Depends(get_db),
):
    service = IdentityAttributeService(db)
    return service.create_attribute(attribute_data)


@router.get("/", response_model=list[IdentityAttributeRead])
def list_identity_attributes(db: Session = Depends(get_db)):
    service = IdentityAttributeService(db)
    return service.list_attributes()


@router.get("/identity/{identity_id}", response_model=list[IdentityAttributeRead])
def list_identity_attributes_by_identity(
    identity_id: str,
    db: Session = Depends(get_db),
):
    service = IdentityAttributeService(db)
    return service.list_attributes_by_identity(identity_id)