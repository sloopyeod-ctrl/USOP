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


def _read_functions():
    return (
        platform_users.list_platform_users,
        platform_users.get_platform_user,
    )


def test_gate_platform_user_inventory_is_not_anonymous():
    for function in _read_functions():
        signature = inspect.signature(function)

        assert "caller" in signature.parameters
        assert isinstance(
            signature.parameters["caller"].default,
            params.Depends,
        )


def test_gate_reads_use_only_canonical_platform_admin_permission():
    for function in _read_functions():
        source = inspect.getsource(function)

        assert source.count(
            '"platform-administration.manage"'
        ) == 1

        forbidden_permission_fragments = (
            "platform-users.read",
            "platform-user.read",
            "platform-administration.read",
            "platform-administrator",
        )

        for fragment in forbidden_permission_fragments:
            assert fragment not in source


def test_gate_browser_cannot_supply_platform_user_caller_identity():
    forbidden_parameters = {
        "caller_id",
        "platform_caller_id",
        "caller_platform_user_id",
        "actor_id",
        "actor",
        "principal_id",
        "subject_id",
        "tenant_id",
    }

    for function in _read_functions():
        signature = inspect.signature(function)

        assert forbidden_parameters.isdisjoint(
            signature.parameters
        )


def test_gate_read_routes_have_no_request_body():
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


def test_gate_foreign_org_inventory_stops_before_service_construction(
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


def test_gate_foreign_org_single_user_stops_before_service_construction(
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
            platform_user_id=USER,
            caller=caller(ORG),
            db=object(),
        )

    assert captured.value.status_code == status.HTTP_404_NOT_FOUND
    assert constructed is False


def test_gate_foreign_org_failures_are_non_enumerating():
    with pytest.raises(HTTPException) as inventory_error:
        platform_users.list_platform_users(
            organization_id=FOREIGN_ORG,
            caller=caller(ORG),
            db=object(),
        )

    with pytest.raises(HTTPException) as user_error:
        platform_users.get_platform_user(
            organization_id=FOREIGN_ORG,
            platform_user_id=USER,
            caller=caller(ORG),
            db=object(),
        )

    assert inventory_error.value.status_code == status.HTTP_404_NOT_FOUND
    assert user_error.value.status_code == status.HTTP_404_NOT_FOUND

    inventory_detail = str(
        inventory_error.value.detail
    ).lower()

    user_detail = str(
        user_error.value.detail
    ).lower()

    forbidden = (
        "foreign",
        "other organization",
        "organization mismatch",
        "caller organization",
        ORG.lower(),
        FOREIGN_ORG.lower(),
    )

    for fragment in forbidden:
        assert fragment not in inventory_detail
        assert fragment not in user_detail


def test_gate_list_read_does_not_mutate_platform_user_state(
    monkeypatch,
):
    expected = [SimpleNamespace(id=USER)]

    class Service:
        def __init__(self, db):
            pass

        def list_for_organization(self, organization_id):
            assert organization_id == ORG
            return expected

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    result = platform_users.list_platform_users(
        organization_id=ORG,
        caller=caller(),
        db=object(),
    )

    assert result is expected

    source = inspect.getsource(
        platform_users.list_platform_users
    )

    forbidden = (
        ".commit(",
        ".rollback(",
        ".flush(",
        "status =",
        "is_active =",
        "activated_at",
        "last_authenticated_at",
        "invite(",
        "suspend(",
        "reactivate(",
        "disable(",
    )

    for fragment in forbidden:
        assert fragment not in source


def test_gate_single_user_read_does_not_mutate_platform_user_state(
    monkeypatch,
):
    expected = SimpleNamespace(id=USER)

    class Service:
        def __init__(self, db):
            pass

        def get_by_id(
            self,
            *,
            organization_id,
            platform_user_id,
        ):
            assert organization_id == ORG
            assert platform_user_id == USER
            return expected

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        Service,
    )

    result = platform_users.get_platform_user(
        organization_id=ORG,
        platform_user_id=USER,
        caller=caller(),
        db=object(),
    )

    assert result is expected

    source = inspect.getsource(
        platform_users.get_platform_user
    )

    forbidden = (
        ".commit(",
        ".rollback(",
        ".flush(",
        "status =",
        "is_active =",
        "activated_at",
        "last_authenticated_at",
        "invite(",
        "suspend(",
        "reactivate(",
        "disable(",
    )

    for fragment in forbidden:
        assert fragment not in source


def test_gate_reads_do_not_inline_runtime_authorization_logic():
    for function in _read_functions():
        source = inspect.getsource(function)

        forbidden = (
            "PlatformRuntimeAuthorizationService",
            ".evaluate(",
            "has_permission(",
            "role_assignment",
            "PlatformRoleAssignment",
            "PlatformRolePermission",
            "PlatformPermission",
        )

        for fragment in forbidden:
            assert fragment not in source


def test_gate_reads_do_not_touch_licensing_or_seat_state():
    for function in _read_functions():
        source = inspect.getsource(function)

        forbidden = (
            "LicenseRepository",
            "LicenseService",
            "SubscriptionState",
            "SeatRepository",
            "seat_allocated",
            "seat_limit",
            "license_identifier",
        )

        for fragment in forbidden:
            assert fragment not in source


def test_gate_single_user_missing_target_remains_non_enumerating_404(
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
    assert captured.value.detail == "Platform User not found."


def test_gate_read_route_contract_is_exact():
    inventory_route = next(
        route
        for route in platform_users.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/"
            "platform-users/"
        )
        and route.methods == {"GET"}
    )

    user_route = next(
        route
        for route in platform_users.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/"
            "platform-users/{platform_user_id}"
        )
        and route.methods == {"GET"}
    )

    assert inventory_route.response_model == list[
        platform_users.PlatformUserRead
    ]

    assert (
        user_route.response_model
        is platform_users.PlatformUserRead
    )

    assert inventory_route.dependant.body_params == []
    assert user_route.dependant.body_params == []
