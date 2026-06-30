from fastapi import APIRouter

from app.core.health import get_health_status, get_ready_status
from app.core.version import APP_NAME, APP_VERSION, ARCHITECTURE

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