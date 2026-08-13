from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.dependencies import runtime_permission
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG = "org-42"
USER = "user-42"
PERMISSION = "platform-administration.manage"


def caller():
    return TrustedPlatformCaller(
        organization_id=ORG,
        platform_user_id=USER,
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-42",
            external_subject_id="subject-42",
        ),
    )


def result(
    *,
    allowed=True,
    organization_id=ORG,
    platform_user_id=USER,
    permission_key=PERMISSION,
):
    return SimpleNamespace(
        allowed=allowed,
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        permission_key=permission_key,
    )


def install_service(monkeypatch, authorization_result):
    captured = {}

    class Service:
        def __init__(self, db):
            captured["db"] = db

        def evaluate(self, **kwargs):
            captured["kwargs"] = kwargs
            return authorization_result

    monkeypatch.setattr(
        runtime_permission,
        "PlatformRuntimeAuthorizationService",
        Service,
    )
    return captured


def test_blank_permission_key_rejected_at_dependency_construction():
    with pytest.raises(ValueError):
        runtime_permission.require_platform_permission("   ")


def test_allow_returns_authenticated_caller(monkeypatch):
    expected = caller()
    captured = install_service(
        monkeypatch,
        result(),
    )

    dependency = runtime_permission.require_platform_permission(
        PERMISSION
    )

    returned = dependency(
        caller=expected,
        db="db-session",
    )

    assert returned is expected
    assert captured["kwargs"] == {
        "organization_id": ORG,
        "platform_user_id": USER,
        "permission_key": PERMISSION,
    }


def test_deny_returns_non_enumerating_403(monkeypatch):
    install_service(
        monkeypatch,
        result(allowed=False),
    )

    dependency = runtime_permission.require_platform_permission(
        PERMISSION
    )

    with pytest.raises(HTTPException) as error:
        dependency(
            caller=caller(),
            db=object(),
        )

    assert error.value.status_code == 403
    assert (
        error.value.detail
        == "Caller is not authorized for this operation."
    )


@pytest.mark.parametrize(
    "authorization_result",
    [
        result(organization_id="org-92"),
        result(platform_user_id="user-92"),
        result(permission_key="different.permission"),
    ],
)
def test_allow_result_context_mismatch_fails_closed(
    monkeypatch,
    authorization_result,
):
    install_service(
        monkeypatch,
        authorization_result,
    )

    dependency = runtime_permission.require_platform_permission(
        PERMISSION
    )

    with pytest.raises(HTTPException) as error:
        dependency(
            caller=caller(),
            db=object(),
        )

    assert error.value.status_code == 403


def test_permission_key_is_closed_over_server_side(monkeypatch):
    captured = install_service(
        monkeypatch,
        result(),
    )

    dependency = runtime_permission.require_platform_permission(
        "  platform-administration.manage  "
    )

    dependency(
        caller=caller(),
        db=object(),
    )

    assert (
        captured["kwargs"]["permission_key"]
        == "platform-administration.manage"
    )
