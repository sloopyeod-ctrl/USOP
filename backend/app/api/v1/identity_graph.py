from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.graph.identity_graph_service import IdentityGraphService

router = APIRouter(
    prefix="/identity-graph",
    tags=["Identity Graph"],
)


@router.get("/{identity_id}")
def get_identity_graph(
    identity_id: str,
    db: Session = Depends(get_db),
):
    service = IdentityGraphService(db)
    return service.get_identity_graph(identity_id)