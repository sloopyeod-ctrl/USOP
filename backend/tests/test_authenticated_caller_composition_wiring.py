from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import authenticated_caller
from app.services.platform_authentication_composition_service import (
    PlatformAuthenticationCompositionError,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG_42 = "org-42"
ORG_92 = "org-92"


def _credentials():
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="signed-token",
    )


def _principal():
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-1",
        external_subject_id="subject-1",
        issuer="https://login.microsoftonline.com/tenant-1/v2.0",
    )


def _caller(principal, organization_id=ORG_42):
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id="platform-user-1",
        principal=principal,
    )


def test_dependency_routes_authenticated_principal_through_composition(monkeypatch):
    principal = _principal()
    expected_caller = _caller(principal)

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal,
    )

    class Composition:
        def __init__(self, db):
            self.db = db

        def resolve_or_accept_invitation(self, *, organization_id, principal):
            assert organization_id == ORG_42
            return SimpleNamespace(caller=expected_caller)

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    result = authenticated_caller.get_authenticated_platform_caller(
        organization_id=ORG_42,
        credentials=_credentials(),
        db=object(),
    )

    assert result is expected_caller


def test_composition_without_caller_still_maps_to_403(monkeypatch):
    principal = _principal()
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal,
    )

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(self, **kwargs):
            return SimpleNamespace(caller=None)

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert error.value.detail == "Caller is not authorized for this Organization."


def test_composition_error_maps_to_non_enumerating_403(monkeypatch):
    principal = _principal()
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal,
    )

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(self, **kwargs):
            raise PlatformAuthenticationCompositionError("failed")

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert error.value.detail == "Caller is not authorized for this Organization."


def test_composition_cannot_return_caller_for_other_org(monkeypatch):
    principal = _principal()
    foreign_caller = _caller(principal, organization_id=ORG_92)

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal,
    )

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(self, **kwargs):
            return SimpleNamespace(caller=foreign_caller)

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert error.value.detail == "Caller Organization context mismatch."


def test_dependency_no_longer_constructs_resolver_directly():
    import inspect

    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    assert "TrustedCallerIdentityService" not in source
    assert "PlatformAuthenticationCompositionService" in source


def test_dependency_still_does_not_perform_runtime_rbac():
    import inspect

    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    for token in (
        "PlatformRuntimeAuthorizationService",
        "permission_key",
        "grant_permission",
        "assign_role",
    ):
        assert token not in source
