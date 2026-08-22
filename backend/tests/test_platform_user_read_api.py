from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, params, status

from app.api.v1 import platform_users
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG = "org-42"
FOREIGN_ORG = "org-92"
USER = "user-42"


def caller(
    organization_id: str = ORG,
) -> TrustedPlatformCaller:
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id="admin-42",
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-42",
            external_subject_id="subject-42",
            issuer="https://issuer.example/v2.0",
        ),
    )


@pytest.mark.parametrize(
    "function_name",
    [
        "list_platform_users",
        "get_platform_user",
    ],
)
def test_platform_user_reads_require_canonical_admin_permission(
    function_name,
):
    source = inspect.getsource(
        getattr(platform_users, function_name)
    )

    assert source.count(
        '"platform-administration.manage"'
    ) == 1


@pytest.mark.parametrize(
    "function_name",
    [
        "list_platform_users",
        "get_platform_user",
    ],
)
def test_platform_user_read_caller_is_server_managed_dependency(
    function_name,
):
    signature = inspect.signature(
        getattr(platform_users, function_name)
    )

    assert "caller" in signature.parameters
    assert isinstance(
        signature.parameters["caller"].default,
        params.Depends,
    )


def test_list_platform_users_reads_only_authorized_organization(
    monkeypatch,
):
    expected = [SimpleNamespace(id=USER)]
    captured = {}

    class Service:
        def __init__(self, db):
            captured["db"] = db

        def list_for_organization(self, organization_id):
            captured["organization_id"] = organization_id
            return expected

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    db = object()

    result = platform_users.list_platform_users(
        organization_id=ORG,
        caller=caller(),
        db=db,
    )

    assert result is expected
    assert captured == {
        "db": db,
        "organization_id": ORG,
    }


def test_get_platform_user_reads_only_authorized_organization(
    monkeypatch,
):
    expected = SimpleNamespace(id=USER)
    captured = {}

    class Service:
        def __init__(self, db):
            captured["db"] = db

        def get_by_id(
            self,
            *,
            organization_id,
            platform_user_id,
        ):
            captured["organization_id"] = organization_id
            captured["platform_user_id"] = platform_user_id
            return expected

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    db = object()

    result = platform_users.get_platform_user(
        organization_id=ORG,
        platform_user_id=USER,
        caller=caller(),
        db=db,
    )

    assert result is expected
    assert captured == {
        "db": db,
        "organization_id": ORG,
        "platform_user_id": USER,
    }


@pytest.mark.parametrize(
    "function_name,kwargs",
    [
        (
            "list_platform_users",
            {},
        ),
        (
            "get_platform_user",
            {
                "platform_user_id": USER,
            },
        ),
    ],
)
def test_platform_user_reads_reject_foreign_route_organization(
    monkeypatch,
    function_name,
    kwargs,
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
        getattr(platform_users, function_name)(
            organization_id=FOREIGN_ORG,
            caller=caller(ORG),
            db=object(),
            **kwargs,
        )

    assert captured.value.status_code == status.HTTP_404_NOT_FOUND
    assert constructed is False


def test_get_platform_user_missing_user_remains_404(
    monkeypatch,
):
    class Service:
        def __init__(self, db):
            pass

        def get_by_id(
            self,
            *,
            organization_id,
            platform_user_id,
        ):
            return None

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    with pytest.raises(HTTPException) as captured:
        platform_users.get_platform_user(
            organization_id=ORG,
            platform_user_id=USER,
            caller=caller(),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_404_NOT_FOUND


def test_platform_user_read_routes_remain_get_without_body():
    expected = {
        (
            "/api/v1/organizations/{organization_id}/"
            "platform-users/"
        ),
        (
            "/api/v1/organizations/{organization_id}/"
            "platform-users/{platform_user_id}"
        ),
    }

    routes = [
        route
        for route in platform_users.router.routes
        if route.path in expected
        and route.methods == {"GET"}
    ]

    assert len(routes) == 2

    for route in routes:
        assert route.dependant.body_params == []
