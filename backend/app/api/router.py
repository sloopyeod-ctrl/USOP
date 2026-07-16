from fastapi import APIRouter

from app.core.health import get_health_status, get_ready_status
from app.core.version import APP_NAME, APP_VERSION, ARCHITECTURE

# API Routers
from app.api.v1.accounts import router as account_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.groups import router as group_router
from app.api.v1.identities import router as identities_router
from app.api.v1.identity_attributes import router as identity_attributes_router
from app.api.v1.memberships import router as membership_router
from app.api.v1.permissions import router as permission_router
from app.api.v1.role_assignments import router as role_assignment_router
from app.api.v1.role_permissions import router as role_permission_router
from app.api.v1.roles import router as role_router
from app.api.v1.access_reviews import router as access_review_router
from app.api.v1.audit_events import router as audit_event_router
from app.api.v1.decision_records import router as decision_record_router
from app.api.v1.review_campaigns import router as review_campaign_router
from app.api.v1.reviewer_workbench import router as reviewer_workbench_router
from app.api.v1.executive_dashboard import router as executive_dashboard_router
from app.api.v1.identity_timeline import router as identity_timeline_router
from app.api.v1.governance_policies import router as governance_policy_router
from app.api.v1.governance_jobs import router as governance_jobs_router
from app.api.v1.connectors import router as connectors_router
from app.api.v1.identity_graph import router as identity_graph_router
from app.api.v1.identity_timeline_v2 import router as identity_timeline_v2_router
from app.api.v1.identity_intelligence import router as identity_intelligence_router
from app.api.v1.organizations import router as organization_router
from app.api.v1.executive_exposure_dashboard import router as executive_exposure_dashboard_router
from app.api.v1.attack_path import router as attack_path_router
from app.api.v1.attack_path_simulation import router as attack_path_simulation_router

router = APIRouter()


# ------------------------------------------------------------------
# Core Endpoints
# ------------------------------------------------------------------

@router.get("/")
def root():
    return {
        "application": APP_NAME,
        "status": "running",
    }


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


# ------------------------------------------------------------------
# API Routers
# ------------------------------------------------------------------

router.include_router(identities_router)
router.include_router(identity_attributes_router)

router.include_router(account_router)
router.include_router(group_router)
router.include_router(membership_router)

router.include_router(role_router)
router.include_router(role_assignment_router)
router.include_router(permission_router)
router.include_router(role_permission_router)

router.include_router(analytics_router)
router.include_router(access_review_router)
router.include_router(audit_event_router)
router.include_router(decision_record_router)
router.include_router(review_campaign_router)
router.include_router(reviewer_workbench_router)
router.include_router(executive_dashboard_router)
router.include_router(identity_timeline_router)
router.include_router(governance_policy_router)
router.include_router(governance_jobs_router)
router.include_router(connectors_router)
router.include_router(identity_graph_router)
router.include_router(identity_timeline_v2_router)
router.include_router(identity_intelligence_router)
router.include_router(organization_router)
router.include_router(executive_exposure_dashboard_router)
router.include_router(attack_path_router)
router.include_router(attack_path_simulation_router)
