from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.intelligence.simulation_service import SimulationService

router = APIRouter(
    prefix="/attack-path",
    tags=["Attack Path Simulation"],
)


class SimulationAction(BaseModel):
    type: str
    account_id: str


class SimulationRequest(BaseModel):
    identity_id: str
    actions: list[SimulationAction]


@router.post("/simulate")
def simulate_attack_path(request: SimulationRequest, db: Session = Depends(get_db)):
    service = SimulationService(db)

    result = service.simulate(
        identity_id=request.identity_id,
        actions=[action.model_dump() for action in request.actions],
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Identity attack path not found")

    return result