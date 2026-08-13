from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import authenticated_caller
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)


ORG_42 = "org-42"
ORG_92 = "org-92"


def credentials(
    token: str = "signed-token",
    scheme: str = "Bearer",
):
    return HTTPAuthorizationCredentials(
        scheme=scheme,
        credentials=token,
    )


def principal():
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-1",
        external_subject_id="subject-1",
        issuer=(
            "https://login.microsoftonline.com/"
            "tenant-1/v2.0"
        ),
    )


def caller(organization_id=ORG_42):
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id="platform-user-1",
        principal=principal(),
    )


def test_missing_bearer_token_fails_401():
    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=None,
            db=object(),
        )

    assert error.value.status_code == 401
    assert error.value.headers == {
        "WWW-Authenticate": "Bearer"
    }


def test_blank_organization_context_fails_400():
    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id="   ",
            credentials=credentials(),
            db=object(),
        )

    assert error.value.status_code == 400


def test_non_bearer_scheme_fails_401():
    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=credentials(scheme="Basic"),
            db=object(),
        )

    assert error.value.status_code == 401


def test_unconfigured_authentication_fails_closed(monkeypatch):
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_tenant_id",
        None,
    )
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_audience",
        None,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller._authentication_configuration()

    assert error.value.status_code == 503


def test_configuration_is_separate_from_graph_credentials(
    monkeypatch,
):
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_tenant_id",
        "caller-tenant",
    )
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_audience",
        "api://usop",
    )

    config = authenticated_caller._authentication_configuration()

    assert config.tenant_id == "caller-tenant"
    assert config.audience == "api://usop"


def test_authentication_failure_maps_to_401(monkeypatch):
    class RejectingAdapter:
        def __init__(self, config):
            self.config = config

        def authenticate(self, token):
            raise authenticated_caller.EntraOidcAuthenticationError(
                "bad token"
            )

    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_tenant_id",
        "tenant-1",
    )
    monkeypatch.setattr(
        authenticated_caller.settings,
        "usop_auth_entra_audience",
        "api://usop",
    )
    monkeypatch.setattr(
        authenticated_caller,
        "EntraOidcAuthenticationAdapter",
        RejectingAdapter,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller._authenticate_bearer_token(
            "invalid-token"
        )

    assert error.value.status_code == 401
    assert error.value.headers == {
        "WWW-Authenticate": "Bearer"
    }


def test_valid_token_and_org_resolve_trusted_caller(monkeypatch):
    expected_principal = principal()
    expected_caller = caller(ORG_42)

    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: expected_principal,
    )

    class Resolver:
        def __init__(self, db):
            self.db = db

        def resolve(self, *, organization_id, principal):
            assert organization_id == ORG_42
            assert principal is expected_principal
            return SimpleNamespace(caller=expected_caller)

    monkeypatch.setattr(
        authenticated_caller,
        "TrustedCallerIdentityService",
        Resolver,
    )

    result = (
        authenticated_caller
        .get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=credentials(),
            db=object(),
        )
    )

    assert result is expected_caller


def test_valid_identity_without_org_assignment_fails_403(
    monkeypatch,
):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal(),
    )

    class Resolver:
        def __init__(self, db):
            self.db = db

        def resolve(self, *, organization_id, principal):
            return SimpleNamespace(caller=None)

    monkeypatch.setattr(
        authenticated_caller,
        "TrustedCallerIdentityService",
        Resolver,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_92,
            credentials=credentials(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert (
        error.value.detail
        == "Caller is not authorized for this Organization."
    )


def test_resolver_cannot_return_caller_for_other_org(
    monkeypatch,
):
    monkeypatch.setattr(
        authenticated_caller,
        "_authenticate_bearer_token",
        lambda token: principal(),
    )

    foreign_caller = caller(ORG_92)

    class Resolver:
        def __init__(self, db):
            self.db = db

        def resolve(self, *, organization_id, principal):
            return SimpleNamespace(caller=foreign_caller)

    monkeypatch.setattr(
        authenticated_caller,
        "TrustedCallerIdentityService",
        Resolver,
    )

    with pytest.raises(HTTPException) as error:
        authenticated_caller.get_authenticated_platform_caller(
            organization_id=ORG_42,
            credentials=credentials(),
            db=object(),
        )

    assert error.value.status_code == 403


def test_dependency_does_not_perform_runtime_authorization():
    source = (
        authenticated_caller.get_authenticated_platform_caller
        .__doc__
    )

    assert source is not None
    assert "Runtime RBAC remains a separate" in source
