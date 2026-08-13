import inspect
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1 import platform_roles
from app.schemas.platform_role_permission import PlatformRolePermissionCreate
from app.services.platform_authorization_service import (
    PROTECTED_PLATFORM_AUTHORITY_PERMISSION_KEY,
    PlatformAuthorizationMappingConflictError,
    PlatformAuthorizationMappingNotFoundError,
    PlatformAuthorizationProtectedPermissionError,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG = "org-42"
ROLE = "role-custom-admin"
PERMISSION = "permission-1"


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


def install_service(monkeypatch, grant_result=None, grant_error=None, remove_error=None):
    captured = {}

    class Service:
        def __init__(self, db):
            captured["db"] = db

        def grant_permission(self, **kwargs):
            captured["grant_kwargs"] = kwargs
            if grant_error is not None:
                raise grant_error
            return grant_result

        def remove_permission(self, **kwargs):
            captured["remove_kwargs"] = kwargs
            if remove_error is not None:
                raise remove_error

    monkeypatch.setattr(platform_roles, "PlatformAuthorizationService", Service)
    return captured


def test_grant_schema_exposes_only_permission_id():
    assert set(PlatformRolePermissionCreate.model_fields) == {
        "platform_permission_id"
    }


def test_grant_forwards_trusted_context(monkeypatch):
    expected = SimpleNamespace(id="mapping-1")
    trusted = caller()
    captured = install_service(monkeypatch, grant_result=expected)

    returned = platform_roles.grant_platform_permission(
        organization_id=ORG,
        platform_role_id=ROLE,
        payload=PlatformRolePermissionCreate(platform_permission_id=PERMISSION),
        caller=trusted,
        db=object(),
    )

    assert returned is expected
    assert captured["grant_kwargs"] == {
        "organization_id": ORG,
        "platform_role_id": ROLE,
        "platform_permission_id": PERMISSION,
        "trusted_caller": trusted,
    }


def test_duplicate_mapping_maps_to_409(monkeypatch):
    install_service(
        monkeypatch,
        grant_error=PlatformAuthorizationMappingConflictError("already mapped"),
    )

    with pytest.raises(HTTPException) as exc:
        platform_roles.grant_platform_permission(
            organization_id=ORG,
            platform_role_id=ROLE,
            payload=PlatformRolePermissionCreate(platform_permission_id=PERMISSION),
            caller=caller(),
            db=object(),
        )

    assert exc.value.status_code == 409


def test_remove_has_no_request_body():
    assert set(inspect.signature(
        platform_roles.remove_platform_permission
    ).parameters) == {
        "organization_id",
        "platform_role_id",
        "platform_permission_id",
        "caller",
        "db",
    }


def test_missing_mapping_is_non_enumerating_404(monkeypatch):
    install_service(
        monkeypatch,
        remove_error=PlatformAuthorizationMappingNotFoundError("missing"),
    )

    with pytest.raises(HTTPException) as exc:
        platform_roles.remove_platform_permission(
            organization_id=ORG,
            platform_role_id=ROLE,
            platform_permission_id=PERMISSION,
            caller=caller(),
            db=object(),
        )

    assert exc.value.status_code == 404


def test_protected_root_removal_maps_to_409(monkeypatch):
    install_service(
        monkeypatch,
        remove_error=PlatformAuthorizationProtectedPermissionError("protected"),
    )

    with pytest.raises(HTTPException) as exc:
        platform_roles.remove_platform_permission(
            organization_id=ORG,
            platform_role_id=ROLE,
            platform_permission_id=PERMISSION,
            caller=caller(),
            db=object(),
        )

    assert exc.value.status_code == 409


def test_root_authority_key_is_exact():
    assert PROTECTED_PLATFORM_AUTHORITY_PERMISSION_KEY == (
        "platform-administration.manage"
    )
