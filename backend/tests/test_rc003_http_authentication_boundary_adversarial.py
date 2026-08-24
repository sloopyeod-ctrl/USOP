from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import authenticated_caller
from app.api.dependencies.runtime_permission import (
    require_platform_permission,
)
from app.api.v1 import platform_users
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)


ORG = "org-42"
FOREIGN_ORG = "org-92"


def principal():
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-42",
        external_subject_id="subject-42",
        issuer="https://issuer.example/v2.0",
    )


def caller(
    organization_id: str = ORG,
):
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id="admin-42",
        principal=principal(),
    )


def credentials(
    token: str = "token",
    scheme: str = "Bearer",
):
    return HTTPAuthorizationCredentials(
        scheme=scheme,
        credentials=token,
    )


def test_gate_missing_bearer_is_401_before_authentication(
    monkeypatch,
):
    called = False

    def forbidden_authenticate(token):
        nonlocal called
        called = True
        raise AssertionError(
            "authentication must not run without credentials"
        )

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        forbidden_authenticate,
    )

    with pytest.raises(HTTPException) as captured:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG,
            credentials=None,
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert captured.value.headers == {
        "WWW-Authenticate": "Bearer"
    }
    assert called is False


def test_gate_non_bearer_scheme_is_401_before_authentication(
    monkeypatch,
):
    called = False

    def forbidden_authenticate(token):
        nonlocal called
        called = True
        raise AssertionError(
            "authentication must not run for non-Bearer scheme"
        )

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        forbidden_authenticate,
    )

    with pytest.raises(HTTPException) as captured:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG,
            credentials=credentials(
                scheme="Basic",
            ),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert captured.value.headers == {
        "WWW-Authenticate": "Bearer"
    }
    assert called is False


def test_gate_cryptographic_authentication_failure_is_generic_401(
    monkeypatch,
):
    class RejectingAdapter:
        def __init__(self, config):
            self.config = config

        def authenticate(self, token):
            raise (
                authenticated_caller
                .EntraOidcAuthenticationError(
                    "specific internal token failure"
                )
            )

    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_tenant_id",
        "tenant-42",
    )
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_audience",
        "api://usop",
    )
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_required_scope",
        "access_as_user",
    )
    monkeypatch.setattr(
        authenticated_caller,
        "EntraOidcAuthenticationAdapter",
        RejectingAdapter,
    )

    with pytest.raises(HTTPException) as captured:
        authenticated_caller._authenticate_bearer_token(
            "bad-token"
        )

    assert captured.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        captured.value.detail
        == "Bearer token authentication failed."
    )
    assert "specific internal" not in captured.value.detail
    assert captured.value.headers == {
        "WWW-Authenticate": "Bearer"
    }


def test_gate_authenticated_unresolved_principal_is_403(
    monkeypatch,
):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal(),
    )

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(
            self,
            *,
            organization_id,
            principal,
        ):
            return SimpleNamespace(caller=None)

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as captured:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG,
            credentials=credentials(),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_403_FORBIDDEN
    assert (
        captured.value.detail
        == "Caller is not authorized for this Organization."
    )


def test_gate_composition_error_is_non_enumerating_403(
    monkeypatch,
):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal(),
    )

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(
            self,
            *,
            organization_id,
            principal,
        ):
            raise (
                authenticated_caller
                .PlatformAuthenticationCompositionError(
                    "sensitive resolution detail"
                )
            )

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as captured:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG,
            credentials=credentials(),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_403_FORBIDDEN
    assert (
        captured.value.detail
        == "Caller is not authorized for this Organization."
    )
    assert "sensitive" not in captured.value.detail


def test_gate_runtime_permission_denial_is_403(
    monkeypatch,
):
    dependency = require_platform_permission(
        "platform-administration.manage"
    )

    class RuntimeAuthorization:
        def __init__(self, db):
            pass

        def evaluate(
            self,
            *,
            organization_id,
            platform_user_id,
            permission_key,
        ):
            return SimpleNamespace(
                allowed=False,
                organization_id=organization_id,
                platform_user_id=platform_user_id,
                permission_key=permission_key,
            )

    import app.api.dependencies.runtime_permission as runtime_permission

    monkeypatch.setattr(
        runtime_permission,
        "PlatformRuntimeAuthorizationService",
        RuntimeAuthorization,
    )

    with pytest.raises(HTTPException) as captured:
        dependency(
            caller=caller(),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_403_FORBIDDEN
    assert (
        captured.value.detail
        == "Caller is not authorized for this operation."
    )


def test_gate_foreign_platform_user_inventory_is_404_before_service(
    monkeypatch,
):
    constructed = False

    class Service:
        def __init__(self, db):
            nonlocal constructed
            constructed = True

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    with pytest.raises(HTTPException) as captured:
        platform_users.list_platform_users(
            organization_id=FOREIGN_ORG,
            caller=caller(ORG),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_404_NOT_FOUND
    assert constructed is False


def test_gate_foreign_platform_user_target_is_non_enumerating_404(
    monkeypatch,
):
    constructed = False

    class Service:
        def __init__(self, db):
            nonlocal constructed
            constructed = True

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    with pytest.raises(HTTPException) as captured:
        platform_users.get_platform_user(
            organization_id=FOREIGN_ORG,
            platform_user_id="foreign-user",
            caller=caller(ORG),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_404_NOT_FOUND
    assert captured.value.detail == "Platform User not found."
    assert constructed is False


def test_gate_http_authentication_does_not_perform_runtime_rbac():
    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    forbidden = (
        "PlatformRuntimeAuthorizationService",
        "platform-administration.manage",
        "PlatformRoleAssignment",
        "PlatformPermission",
    )

    for fragment in forbidden:
        assert fragment not in source


def test_gate_runtime_permission_inherits_server_resolved_caller():
    source = inspect.getsource(
        require_platform_permission
    )

    assert "get_authenticated_platform_caller" in source
    assert "caller.platform_user_id" in source
    assert "caller.organization_id" in source


def test_gate_platform_user_reads_require_server_defined_admin_permission():
    for function in (
        platform_users.list_platform_users,
        platform_users.get_platform_user,
    ):
        source = inspect.getsource(function)

        assert (
            '"platform-administration.manage"'
            in source
        )


def test_gate_http_boundary_does_not_allocate_seats_or_touch_licensing():
    sources = (
        inspect.getsource(
            authenticated_caller.get_authenticated_platform_caller
        ),
        inspect.getsource(
            require_platform_permission
        ),
        inspect.getsource(
            platform_users.list_platform_users
        ),
        inspect.getsource(
            platform_users.get_platform_user
        ),
    )

    forbidden = (
        "LicenseRepository",
        "LicenseService",
        "SeatRepository",
        "seat_allocated",
        "seat_limit",
    )

    for source in sources:
        for fragment in forbidden:
            assert fragment not in source
