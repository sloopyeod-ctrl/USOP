from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1 import platform_users
from app.schemas.platform_role_assignment import PlatformRoleAssignmentCreate
from app.services.platform_authorization_service import (
    PlatformAuthorizationAssignmentConflictError,
    PlatformAuthorizationAssignmentWindowError,
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationRoleNotActiveError,
    PlatformAuthorizationUserNotAssignableError,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG_42 = "org-42"
TARGET_USER = "target-user"
ROLE_ID = "role-admin"
ACTOR_USER = "admin-user"


def caller():
    return TrustedPlatformCaller(
        organization_id=ORG_42,
        platform_user_id=ACTOR_USER,
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-42",
            external_subject_id="subject-admin",
        ),
    )


def assignment():
    now = datetime.now(UTC)
    return SimpleNamespace(
        id="assignment-1",
        organization_id=ORG_42,
        platform_user_id=TARGET_USER,
        platform_role_id=ROLE_ID,
        assigned_at=now,
        expires_at=None,
        created_at=now,
        updated_at=now,
        created_by=f"platform-user:{ACTOR_USER}",
        updated_by=f"platform-user:{ACTOR_USER}",
        is_active=True,
    )


def install_service(monkeypatch, result=None, error=None):
    captured = {}

    class Service:
        def __init__(self, db):
            captured["db"] = db

        def assign_role(self, **kwargs):
            captured["kwargs"] = kwargs
            if error is not None:
                raise error
            return result

    monkeypatch.setattr(platform_users, "PlatformAuthorizationService", Service)
    return captured


def test_success_forwards_target_and_trusted_caller(monkeypatch):
    expected = assignment()
    captured = install_service(monkeypatch, result=expected)
    trusted = caller()

    returned = platform_users.assign_platform_role(
        organization_id=ORG_42,
        platform_user_id=TARGET_USER,
        payload=PlatformRoleAssignmentCreate(platform_role_id=ROLE_ID),
        caller=trusted,
        db="db-session",
    )

    assert returned is expected
    assert captured["kwargs"] == {
        "organization_id": ORG_42,
        "platform_user_id": TARGET_USER,
        "platform_role_id": ROLE_ID,
        "expires_at": None,
        "trusted_caller": trusted,
    }


def test_create_schema_exposes_only_target_role_and_expiration():
    assert set(PlatformRoleAssignmentCreate.model_fields) == {
        "platform_role_id",
        "expires_at",
    }


def test_cross_org_boundary_maps_to_non_enumerating_404(monkeypatch):
    install_service(
        monkeypatch,
        error=PlatformAuthorizationOrganizationBoundaryError("foreign"),
    )

    with pytest.raises(HTTPException) as exc:
        platform_users.assign_platform_role(
            organization_id=ORG_42,
            platform_user_id=TARGET_USER,
            payload=PlatformRoleAssignmentCreate(platform_role_id=ROLE_ID),
            caller=caller(),
            db=object(),
        )

    assert exc.value.status_code == 404


def test_duplicate_assignment_maps_to_409(monkeypatch):
    install_service(
        monkeypatch,
        error=PlatformAuthorizationAssignmentConflictError("already assigned"),
    )

    with pytest.raises(HTTPException) as exc:
        platform_users.assign_platform_role(
            organization_id=ORG_42,
            platform_user_id=TARGET_USER,
            payload=PlatformRoleAssignmentCreate(platform_role_id=ROLE_ID),
            caller=caller(),
            db=object(),
        )

    assert exc.value.status_code == 409


@pytest.mark.parametrize(
    "error",
    [
        PlatformAuthorizationUserNotAssignableError("suspended"),
        PlatformAuthorizationRoleNotActiveError("disabled"),
        PlatformAuthorizationAssignmentWindowError("bad window"),
    ],
)
def test_invalid_assignment_state_maps_to_400(monkeypatch, error):
    install_service(monkeypatch, error=error)

    with pytest.raises(HTTPException) as exc:
        platform_users.assign_platform_role(
            organization_id=ORG_42,
            platform_user_id=TARGET_USER,
            payload=PlatformRoleAssignmentCreate(
                platform_role_id=ROLE_ID,
                expires_at=datetime.now(UTC) - timedelta(minutes=1),
            ),
            caller=caller(),
            db=object(),
        )

    assert exc.value.status_code == 400
