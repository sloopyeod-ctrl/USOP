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


ORG_A = "org-a"
ORG_B = "org-b"
ADMIN_A = "admin-a"


def _caller(
    *,
    organization_id: str = ORG_A,
    platform_user_id: str = ADMIN_A,
):
    return SimpleNamespace(
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        principal=SimpleNamespace(),
    )


def _payload(**overrides):
    values = {
        "display_name": "Jane Smith",
        "email": "jane@example.com",
        "identity_provider": "microsoft-entra",
        "external_tenant_id": "tenant-a",
        "external_subject_id": "subject-jane",
        "identity_issuer": "https://issuer.example/tenant-a",
    }
    values.update(overrides)
    return PlatformUserInvite(**values)


def _service(monkeypatch):
    service = MagicMock()
    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        lambda db: service,
    )
    return service


def test_gate_invitation_route_requires_canonical_admin_permission():
    source = inspect.getsource(
        platform_users.invite_platform_user
    )

    assert source.count(
        '"platform-administration.manage"'
    ) == 1


def test_gate_caller_dependency_is_server_managed():
    signature = inspect.signature(
        platform_users.invite_platform_user
    )

    caller = signature.parameters["caller"]
    assert isinstance(caller.default, params.Depends)


def test_gate_endpoint_has_no_client_actor_or_lifecycle_operands():
    signature = inspect.signature(
        platform_users.invite_platform_user
    )

    forbidden = {
        "actor",
        "created_by",
        "updated_by",
        "status",
        "created_via_bootstrap",
        "organizational_identity_id",
        "platform_role_id",
        "permission_key",
        "seat_allocated",
        "authorization_granted",
        "activated_at",
        "last_authenticated_at",
        "timestamp",
        "evaluated_at",
        "now",
    }

    assert forbidden.isdisjoint(signature.parameters)


def test_gate_body_schema_forbids_authority_injection():
    with pytest.raises(ValidationError):
        PlatformUserInvite(
            display_name="Jane Smith",
            email="jane@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-jane",
            created_via_bootstrap=True,
        )


def test_gate_body_schema_forbids_role_injection():
    with pytest.raises(ValidationError):
        PlatformUserInvite(
            display_name="Jane Smith",
            email="jane@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-jane",
            platform_role_id="role-admin",
        )


def test_gate_trusted_caller_is_passed_through_unchanged(monkeypatch):
    service = _service(monkeypatch)
    caller = _caller()
    result = SimpleNamespace(id="user-1")
    service.invite.return_value = result

    response = platform_users.invite_platform_user(
        organization_id=ORG_A,
        payload=_payload(),
        caller=caller,
        db=MagicMock(),
    )

    assert response is result
    kwargs = service.invite.call_args.kwargs
    assert kwargs["trusted_caller"] is caller


def test_gate_router_does_not_rewrite_cross_org_caller(monkeypatch):
    service = _service(monkeypatch)
    caller = _caller(organization_id=ORG_B)

    service.invite.side_effect = (
        PlatformUserOrganizationBoundaryError(
            "cross-tenant caller"
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_A,
            payload=_payload(),
            caller=caller,
            db=MagicMock(),
        )

    kwargs = service.invite.call_args.kwargs
    assert kwargs["trusted_caller"] is caller
    assert kwargs["organization_id"] == ORG_A
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformUserOrganizationNotFoundError,
        PlatformUserOrganizationBoundaryError,
    ],
)
def test_gate_not_found_errors_are_uniform_and_non_leaking(
    monkeypatch,
    error_type,
):
    service = _service(monkeypatch)
    service.invite.side_effect = error_type(
        "tenant-sensitive internal detail"
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_A,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == (
        "Requested Platform User invitation target was not found."
    )
    assert "tenant-sensitive" not in exc_info.value.detail


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformUserExternalIdentityConflictError,
        PlatformUserInvitationConflictError,
    ],
)
def test_gate_conflicts_never_become_success(
    monkeypatch,
    error_type,
):
    service = _service(monkeypatch)
    service.invite.side_effect = error_type(
        "invitation conflict"
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_A,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformUserOrganizationNotActiveError,
        PlatformUserInvitationValidationError,
    ],
)
def test_gate_validation_failures_never_become_success(
    monkeypatch,
    error_type,
):
    service = _service(monkeypatch)
    service.invite.side_effect = error_type(
        "invalid invitation"
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.invite_platform_user(
            organization_id=ORG_A,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_gate_unexpected_internal_failure_is_not_reclassified(
    monkeypatch,
):
    service = _service(monkeypatch)
    service.invite.side_effect = RuntimeError(
        "unexpected failure"
    )

    with pytest.raises(RuntimeError, match="unexpected failure"):
        platform_users.invite_platform_user(
            organization_id=ORG_A,
            payload=_payload(),
            caller=_caller(),
            db=MagicMock(),
        )


def test_gate_router_does_not_reimplement_invitation_policy():
    source = inspect.getsource(
        platform_users.invite_platform_user
    )

    forbidden = [
        "PlatformUserStatus.",
        "created_via_bootstrap",
        "organizational_identity_id",
        "get_by_external_identity(",
        "get_by_id_for_update(",
        "record_pending(",
        "commit(",
        "rollback(",
        "datetime.now",
        "has_permission(",
    ]

    for fragment in forbidden:
        assert fragment not in source


def test_gate_route_is_exactly_one_post_root_mutation():
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


def test_gate_route_has_only_invitation_body_model():
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


def test_gate_payload_cannot_smuggle_organization_id():
    with pytest.raises(ValidationError):
        PlatformUserInvite(
            display_name="Jane Smith",
            email="jane@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-jane",
            organization_id=ORG_B,
        )


def test_gate_payload_cannot_smuggle_actor_identity():
    with pytest.raises(ValidationError):
        PlatformUserInvite(
            display_name="Jane Smith",
            email="jane@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-jane",
            actor="platform-user:evil",
        )


def test_gate_endpoint_forwards_only_schema_identity_fields(monkeypatch):
    service = _service(monkeypatch)
    service.invite.return_value = SimpleNamespace(id="user-1")

    platform_users.invite_platform_user(
        organization_id=ORG_A,
        payload=_payload(),
        caller=_caller(),
        db=MagicMock(),
    )

    kwargs = service.invite.call_args.kwargs

    assert set(kwargs) == {
        "organization_id",
        "display_name",
        "email",
        "identity_provider",
        "external_tenant_id",
        "external_subject_id",
        "identity_issuer",
        "trusted_caller",
    }


def test_gate_endpoint_does_not_call_runtime_permission_evaluator_itself():
    source = inspect.getsource(
        platform_users.invite_platform_user
    )

    assert "PlatformRuntimeAuthorizationService" not in source
    assert "has_permission(" not in source
