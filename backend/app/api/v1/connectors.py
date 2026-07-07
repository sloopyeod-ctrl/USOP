from fastapi import APIRouter

from app.services.connector_service import ConnectorService

router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"],
)

service = ConnectorService()


@router.get("/")
def list_connectors():
    return service.list_connectors()


@router.get("/{connector_name}/collect")
def collect(connector_name: str):
    return service.collect(connector_name)


@router.post("/{connector_name}/synchronize")
def synchronize(connector_name: str):
    return service.synchronize(connector_name)