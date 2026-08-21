import inspect
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


ORG_A = "org-a"
ORG_B = "org-b"


def _credentials(token="signed-token"):
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def _principal():
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-a",
        issuer="issuer-a",
    )


def _caller(organization_id=ORG_A):
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id="user-a",
        principal=_principal(),
    )


def test_gate_dependency_has_no_direct_resolver_fallback():
    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    assert "TrustedCallerIdentityService" not in source
    assert "PlatformAuthenticationCompositionService" in source


def test_gate_browser_cannot_supply_platform_user_identifier():
    signature = inspect.signature(
        authenticated_caller.get_authenticated_platform_caller
    )

    assert "platform_user_id" not in signature.parameters
    assert "user_id" not in signature.parameters
    assert "caller_id" not in signature.parameters


def test_gate_dependency_does_not_accept_invitation_state_from_request():
    signature = inspect.signature(
        authenticated_caller.get_authenticated_platform_caller
    )

    forbidden = (
        "status",
        "platform_user_status",
        "invited",
        "invitation",
        "identity_provider",
        "external_tenant_id",
        "external_subject_id",
    )

    for name in forbidden:
        assert name not in signature.parameters


def test_gate_composition_failure_is_non_enumerating_403(monkeypatch):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: _principal(),
    )

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(self, **kwargs):
            raise PlatformAuthenticationCompositionError(
                "Invitation exists but failed after acceptance."
            )

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_A,
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert error.value.detail == (
        "Caller is not authorized for this Organization."
    )
    assert "invitation" not in error.value.detail.lower()
    assert "active" not in error.value.detail.lower()
    assert "issuer" not in error.value.detail.lower()


def test_gate_unresolved_composition_is_non_enumerating_403(monkeypatch):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: _principal(),
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
            organization_id=ORG_A,
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert error.value.detail == (
        "Caller is not authorized for this Organization."
    )


def test_gate_foreign_org_caller_is_rejected_after_composition(monkeypatch):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: _principal(),
    )

    foreign = _caller(ORG_B)

    class Composition:
        def __init__(self, db):
            pass

        def resolve_or_accept_invitation(self, **kwargs):
            return SimpleNamespace(caller=foreign)

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_A,
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert error.value.detail == (
        "Caller Organization context mismatch."
    )


def test_gate_dependency_does_not_perform_runtime_authorization():
    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    forbidden = (
        "PlatformRuntimeAuthorizationService",
        "PlatformAuthorizationService",
        "permission_key",
        "grant_permission",
        "assign_role",
        "platform-administration.manage",
    )

    for token in forbidden:
        assert token not in source


def test_gate_dependency_does_not_allocate_seats_or_touch_licensing():
    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    forbidden = (
        "SeatRepository",
        "LicenseRepository",
        "seat_allocated",
        "license_id",
    )

    for token in forbidden:
        assert token not in source


def test_gate_dependency_does_not_mutate_platform_user_lifecycle():
    source = inspect.getsource(
        authenticated_caller.get_authenticated_platform_caller
    )

    forbidden = (
        ".status =",
        ".activated_at =",
        ".last_authenticated_at =",
        "record_first_authentication",
    )

    for token in forbidden:
        assert token not in source


def test_gate_dependency_uses_route_organization_only_for_scope(monkeypatch):
    principal = _principal()
    observed = {}

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal,
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
            observed["organization_id"] = organization_id
            observed["principal"] = principal
            return SimpleNamespace(
                caller=_caller(ORG_A)
            )

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    result = authenticated_caller.get_authenticated_platform_caller(
        organization_id=ORG_A,
        credentials=_credentials(),
        db=object(),
    )

    assert result.organization_id == ORG_A
    assert observed["organization_id"] == ORG_A
    assert observed["principal"] is principal


def test_gate_missing_bearer_stops_before_composition(monkeypatch):
    composition = MagicComposition = SimpleNamespace(
        constructed=False
    )

    class Composition:
        def __init__(self, db):
            composition.constructed = True

    monkeypatch.setattr(
        authenticated_caller,
        "PlatformAuthenticationCompositionService",
        Composition,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_A,
            credentials=None,
            db=object(),
        )

    assert error.value.status_code == 401
    assert composition.constructed is False


def test_gate_blank_organization_stops_before_authentication(monkeypatch):
    called = {"authenticate": False}

    def authenticate(token):
        called["authenticate"] = True
        return _principal()

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        authenticate,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id="   ",
            credentials=_credentials(),
            db=object(),
        )

    assert error.value.status_code == 400
    assert called["authenticate"] is False


def test_gate_dependency_preserves_runtime_rbac_separation_contract():
    doc = (
        authenticated_caller
        .get_authenticated_platform_caller
        .__doc__
    )

    assert doc is not None
    assert "Runtime RBAC remains a separate authorization boundary." in doc
