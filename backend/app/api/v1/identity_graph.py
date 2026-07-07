from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.graph.identity_graph_service import IdentityGraphService
from app.graph.graph_difference_engine import GraphDifferenceEngine

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

@router.get("/{identity_id}/diff-test")
def test_identity_graph_diff(
    identity_id: str,
    db: Session = Depends(get_db),
):
    service = IdentityGraphService(db)
    diff_engine = GraphDifferenceEngine(db)

    before = service.get_identity_graph(identity_id)
    after = service.get_identity_graph(identity_id)

    return diff_engine.compare(before, after)