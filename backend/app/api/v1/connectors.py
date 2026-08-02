from fastapi import APIRouter

from app.schemas.provider import ProviderDescriptorRead
from app.services.connector_service import ConnectorService
from app.schemas.connector_health import ConnectorHealthRead


router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"],
)

service = ConnectorService()


@router.get(
    "/",
    response_model=list[str],
)
def list_connectors():
    """
    Return canonical identifiers for active connector providers.

    This compatibility endpoint reports runtime provider activation rather
    than every provider type known to the registry.
    """

    return service.list_connectors()


@router.get(
    "/providers",
    response_model=list[ProviderDescriptorRead],
)
def list_provider_catalog():
    """
    Return the read-only catalog of registered connector provider types.

    Catalog presence does not imply that a provider is licensed, configured,
    enabled, authenticated, healthy, or synchronized for an organization.
    """

    return service.list_provider_descriptors()


@router.get(
    "/health",
    response_model=list[ConnectorHealthRead],
)
def list_connector_health():
    """
    Return current operational health for active connector providers.

    Health is evaluated when this endpoint is requested.

    The result does not represent persistent synchronization history.
    """

    return service.health()

@router.get(
    "/{connector_name}/collect",
)
def collect(
    connector_name: str,
):
    return service.collect(
        connector_name
    )


@router.post(
    "/{connector_name}/synchronize",
)
def synchronize(
    connector_name: str,
):
    return service.synchronize(
        connector_name
    )
