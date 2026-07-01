from fastapi import APIRouter

from app.core.health import get_health_status, get_ready_status
from app.core.version import APP_NAME, APP_VERSION, ARCHITECTURE
from app.api.v1.identities import router as identities_router

router = APIRouter()


@router.get("/")
def root():
    return {"application": APP_NAME, "status": "running"}


@router.get("/health")
def health():
    return get_health_status()


@router.get("/ready")
def ready():
    return get_ready_status()


@router.get("/version")
def version():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "architecture": ARCHITECTURE,
    }

router.include_router(identities_router)