from fastapi import APIRouter

from app.core.health import get_health_status, get_ready_status
from app.core.version import APP_NAME, APP_VERSION, ARCHITECTURE
from app.api.v1.identities import router as identities_router
from app.api.v1.identity_attributes import router as identity_attributes_router
from app.api.v1.accounts import router as account_router
from app.api.v1.groups import router as group_router
from app.api.v1.memberships import router as membership_router

router = APIRouter()
router.include_router(identity_attributes_router)
router.include_router(account_router)

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
router.include_router(identity_attributes_router)
router.include_router(group_router)
router.include_router(membership_router)