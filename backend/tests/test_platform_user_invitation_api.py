import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, params, status
from pydantic import ValidationError

from app.api.v1 import platform_users
from app.schemas.platform_user import PlatformUserInvite
from app.services.platform_user_service import (
    PlatformUserExternalIdentityConflictError,
    PlatformUserInvitationConflictError,
    PlatformUserInvitationValidationError,
    PlatformUserOrganizationBoundaryError,
    PlatformUserOrganizationNotActiveError,
    PlatformUserOrganizationNotFoundError,
)


ORG_ID = "org-a"


def _caller():
    return SimpleNamespace(
        organization_id=ORG_ID,
        platform_user_id="admin-a",
        principal=SimpleNamespace(),
    )


def _payload():
    return PlatformUserInvite(
        display_name="Jane Smith",
        email="jane@example.com",
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-jane",
        identity_issuer="https://issuer.example/tenant-a",
    )


def test_invitation_endpoint_delegates_to_service(monkeypatch):
    service = MagicMock()
    result = SimpleNamespace(id="user-1")
    service.invite.return_value = result
    monkeypatch.setattr(platform_users, "PlatformUserService", lambda db: service)

    caller = _caller()
    response = platform_users.invite_platform_user(
        organization_id=ORG_ID,
        payload=_payload(),
        caller=caller,
        db=MagicMock(),
    )

    assert response is result
    service.invite.assert_called_once_with(
        organization_id=ORG_ID,
        display_name="Jane Smith",
        email="jane@example.com",
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-jane",
        identity_issuer="https://issuer.example/tenant-a",
        trusted_caller=caller,
    )


def test_invitation_endpoint_uses_canonical_admin_permission():
    source = inspect.getsource(platform_users.invite_platform_user)
    assert '"platform-administration.manage"' in source


def test_invitation_endpoint_caller_is_server_managed_dependency():
    signature = inspect.signature(platform_users.invite_platform_user)
    assert set(signature.parameters) == {
        "organization_id", "payload", "caller", "db"
    }
    assert isinstance(signature.parameters["caller"].default, params.Depends)


def test_invitation_schema_forbids_authority_fields():
    with pytest.raises(ValidationError):
        PlatformUserInvite(
            display_name="Jane Smith",
            email="jane@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-jane",
            status="Active",
        )


@pytest.mark.parametrize(
    "error_type",
    [PlatformUserOrganizationNotFoundError, PlatformUserOrganizationBoundaryError],
)
def test_invitation_not_found_boundary_maps_to_404(monkeypatch, error_type):
    service = MagicMock()
    service.invite.side_effect = error_type("tenant-sensitive detail")
    monkeypatch.setattr(platform_users, "PlatformUserService", lambda db: service)

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_ID,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == (
        "Requested Platform User invitation target was not found."
    )


@pytest.mark.parametrize(
    "error_type",
    [PlatformUserExternalIdentityConflictError, PlatformUserInvitationConflictError],
)
def test_invitation_conflict_maps_to_409(monkeypatch, error_type):
    service = MagicMock()
    service.invite.side_effect = error_type("invitation conflict")
    monkeypatch.setattr(platform_users, "PlatformUserService", lambda db: service)

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_ID,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "error_type",
    [PlatformUserOrganizationNotActiveError, PlatformUserInvitationValidationError],
)
def test_invitation_validation_maps_to_400(monkeypatch, error_type):
    service = MagicMock()
    service.invite.side_effect = error_type("invalid invitation")
    monkeypatch.setattr(platform_users, "PlatformUserService", lambda db: service)

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_ID,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_invitation_route_is_post_root_and_returns_201():
    matches = [
        route
        for route in platform_users.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/platform-users/"
        )
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    assert matches[0].status_code == status.HTTP_201_CREATED
    assert matches[0].response_model is platform_users.PlatformUserRead


def test_invitation_route_has_exactly_one_body_model():
    route = next(
        route
        for route in platform_users.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/platform-users/"
        )
        and route.methods == {"POST"}
    )
    assert len(route.dependant.body_params) == 1

    body_param = route.dependant.body_params[0]
    assert body_param.name == "payload"
    assert body_param.field_info.annotation is PlatformUserInvite
