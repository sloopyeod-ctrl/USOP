import inspect
import pytest
from fastapi import HTTPException

from app.api.v1 import platform_users
from app.services.platform_authorization_service import (
    PlatformAuthorizationAssignmentNotFoundError,
    PlatformAuthorizationOrganizationBoundaryError,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller

ORG = "org-42"
USER = "target-user"
ROLE = "role-admin"


def caller():
    return TrustedPlatformCaller(
        organization_id=ORG,
        platform_user_id="admin-user",
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-42",
            external_subject_id="subject-admin",
        ),
    )


def install(monkeypatch, error=None):
    captured = {}
    class Service:
        def __init__(self, db):
            captured["db"] = db
        def remove_role(self, **kwargs):
            captured["kwargs"] = kwargs
            if error:
                raise error
    monkeypatch.setattr(platform_users, "PlatformAuthorizationService", Service)
    return captured


def test_removal_forwards_trusted_actor_and_route_targets(monkeypatch):
    captured = install(monkeypatch)
    trusted = caller()
    assert platform_users.remove_platform_role(
        organization_id=ORG,
        platform_user_id=USER,
        platform_role_id=ROLE,
        caller=trusted,
        db=object(),
    ) is None
    assert captured["kwargs"] == {
        "organization_id": ORG,
        "platform_user_id": USER,
        "platform_role_id": ROLE,
        "trusted_caller": trusted,
    }


def test_removal_has_no_request_body():
    assert set(inspect.signature(
        platform_users.remove_platform_role
    ).parameters) == {
        "organization_id",
        "platform_user_id",
        "platform_role_id",
        "caller",
        "db",
    }


@pytest.mark.parametrize("error", [
    PlatformAuthorizationOrganizationBoundaryError("foreign"),
    PlatformAuthorizationAssignmentNotFoundError("missing"),
])
def test_foreign_or_missing_assignment_is_non_enumerating_404(
    monkeypatch, error
):
    install(monkeypatch, error)
    with pytest.raises(HTTPException) as exc:
        platform_users.remove_platform_role(
            organization_id=ORG,
            platform_user_id=USER,
            platform_role_id=ROLE,
            caller=caller(),
            db=object(),
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == (
        "Requested Platform authorization target was not found."
    )
