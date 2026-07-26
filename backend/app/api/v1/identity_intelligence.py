from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.identity_intelligence_service import (
    IdentityIntelligenceService,
)


router = APIRouter(
    tags=["Identity Intelligence"],
)


@router.get(
    "/identity-intelligence/{identity_id}"
)
def get_identity_intelligence(
    identity_id: str,
    db: Session = Depends(get_db),
):
    """
    Legacy organization-neutral intelligence projection.

    Organization-owned decision state is intentionally omitted.
    """

    service = IdentityIntelligenceService(db)

    return service.get_identity_intelligence(
        identity_id
    )


@router.get(
    (
        "/api/v1/organizations/"
        "{organization_id}/identity-intelligence/"
        "{identity_id}"
    )
)
def get_organization_identity_intelligence(
    organization_id: str,
    identity_id: str,
    db: Session = Depends(get_db),
):
    """
    Organization-scoped identity intelligence with authoritative
    recommendation disposition.
    """

    service = IdentityIntelligenceService(db)

    return service.get_identity_intelligence(
        identity_id,
        organization_id=organization_id,
    )
