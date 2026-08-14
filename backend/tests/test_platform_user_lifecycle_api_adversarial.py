import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, params, status

from app.api.v1 import platform_users
from app.services.platform_user_service import (
    PlatformUserInvalidLifecycleTransitionError,
    PlatformUserLastEffectiveAdministratorError,
    PlatformUserNotFoundError,
    PlatformUserOrganizationBoundaryError,
    PlatformUserOrganizationNotFoundError,
)


ORG_A = "org-a"
ORG_B = "org-b"
USER_A = "user-a"
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


def _mock_service(monkeypatch):
    service = MagicMock()
    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        lambda db: service,
    )
    return service


@pytest.mark.parametrize(
    ("function_name", "operation_name"),
    [
        ("suspend_platform_user", "suspend"),
        ("reactivate_platform_user", "reactivate"),
        ("disable_platform_user", "disable"),
    ],
)
def test_gate_endpoint_passes_trusted_caller_unchanged(
    monkeypatch,
    function_name,
    operation_name,
):
    service = _mock_service(monkeypatch)
    caller = _caller()
    result = SimpleNamespace(id=USER_A)
    getattr(service, operation_name).return_value = result

    response = getattr(platform_users, function_name)(
        organization_id=ORG_A,
        platform_user_id=USER_A,
        caller=caller,
        db=MagicMock(),
    )

    assert response is result
    kwargs = getattr(service, operation_name).call_args.kwargs
    assert kwargs["trusted_caller"] is caller
    assert kwargs["organization_id"] == ORG_A
    assert kwargs["platform_user_id"] == USER_A


@pytest.mark.parametrize(
    "function_name",
    [
        "suspend_platform_user",
        "reactivate_platform_user",
        "disable_platform_user",
    ],
)
def test_gate_no_http_payload_can_inject_actor_or_status(
    function_name,
):
    signature = inspect.signature(
        getattr(platform_users, function_name)
    )

    forbidden = {
        "actor",
        "updated_by",
        "status",
        "new_status",
        "is_active",
        "evaluated_at",
        "timestamp",
        "now",
    }

    assert forbidden.isdisjoint(signature.parameters)


@pytest.mark.parametrize(
    "function_name",
    [
        "suspend_platform_user",
        "reactivate_platform_user",
        "disable_platform_user",
    ],
)
def test_gate_caller_dependency_is_required_and_server_managed(
    function_name,
):
    signature = inspect.signature(
        getattr(platform_users, function_name)
    )
    caller_param = signature.parameters["caller"]

    assert isinstance(caller_param.default, params.Depends)
    assert caller_param.annotation is platform_users.TrustedPlatformCaller


@pytest.mark.parametrize(
    "function_name",
    [
        "suspend_platform_user",
        "reactivate_platform_user",
        "disable_platform_user",
    ],
)
def test_gate_canonical_permission_string_is_present_once(
    function_name,
):
    source = inspect.getsource(
        getattr(platform_users, function_name)
    )

    assert source.count(
        '"platform-administration.manage"'
    ) == 1


@pytest.mark.parametrize(
    ("error_type", "operation_name"),
    [
        (PlatformUserOrganizationNotFoundError, "suspend"),
        (PlatformUserNotFoundError, "suspend"),
        (PlatformUserOrganizationBoundaryError, "suspend"),
        (PlatformUserOrganizationNotFoundError, "reactivate"),
        (PlatformUserNotFoundError, "reactivate"),
        (PlatformUserOrganizationBoundaryError, "reactivate"),
        (PlatformUserOrganizationNotFoundError, "disable"),
        (PlatformUserNotFoundError, "disable"),
        (PlatformUserOrganizationBoundaryError, "disable"),
    ],
)
def test_gate_not_found_errors_are_uniform_and_do_not_leak_detail(
    monkeypatch,
    error_type,
    operation_name,
):
    service = _mock_service(monkeypatch)
    getattr(service, operation_name).side_effect = error_type(
        "tenant-sensitive internal detail"
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users._run_platform_user_lifecycle_operation(
            operation=operation_name,
            organization_id=ORG_A,
            platform_user_id=USER_A,
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == (
        "Requested Platform User lifecycle target was not found."
    )
    assert "tenant-sensitive" not in exc_info.value.detail


@pytest.mark.parametrize(
    ("error_type", "operation_name"),
    [
        (PlatformUserInvalidLifecycleTransitionError, "suspend"),
        (PlatformUserLastEffectiveAdministratorError, "suspend"),
        (PlatformUserInvalidLifecycleTransitionError, "reactivate"),
        (PlatformUserLastEffectiveAdministratorError, "disable"),
    ],
)
def test_gate_lifecycle_conflicts_never_become_success(
    monkeypatch,
    error_type,
    operation_name,
):
    service = _mock_service(monkeypatch)
    getattr(service, operation_name).side_effect = error_type(
        "blocked lifecycle operation"
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users._run_platform_user_lifecycle_operation(
            operation=operation_name,
            organization_id=ORG_A,
            platform_user_id=USER_A,
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "blocked lifecycle operation"


def test_gate_helper_does_not_reimplement_lifecycle_policy():
    source = inspect.getsource(
        platform_users._run_platform_user_lifecycle_operation
    )

    forbidden_fragments = [
        "PlatformUserStatus.",
        "is_active",
        "has_permission(",
        "platform-administration.manage",
        "datetime.now",
        "commit(",
        "rollback(",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_gate_router_contains_exactly_three_lifecycle_mutation_routes():
    lifecycle_suffixes = {
        "/suspend",
        "/reactivate",
        "/disable",
    }

    lifecycle_routes = [
        route
        for route in platform_users.router.routes
        if any(
            route.path.endswith(suffix)
            for suffix in lifecycle_suffixes
        )
    ]

    assert len(lifecycle_routes) == 3
    assert {
        route.path.rsplit("/", 1)[-1]
        for route in lifecycle_routes
    } == {"suspend", "reactivate", "disable"}

    for route in lifecycle_routes:
        assert route.methods == {"POST"}


def test_gate_lifecycle_routes_have_no_body_model():
    lifecycle_paths = {
        "/api/v1/organizations/{organization_id}/platform-users/"
        "{platform_user_id}/suspend",
        "/api/v1/organizations/{organization_id}/platform-users/"
        "{platform_user_id}/reactivate",
        "/api/v1/organizations/{organization_id}/platform-users/"
        "{platform_user_id}/disable",
    }

    for route in platform_users.router.routes:
        if route.path not in lifecycle_paths:
            continue

        body_params = [
            dependant
            for dependant in route.dependant.body_params
        ]
        assert body_params == []


def test_gate_service_internal_failure_is_not_reclassified():
    service = MagicMock()
    service.suspend.side_effect = RuntimeError(
        "unexpected service failure"
    )

    original = platform_users.PlatformUserService
    platform_users.PlatformUserService = lambda db: service

    try:
        with pytest.raises(
            RuntimeError,
            match="unexpected service failure",
        ):
            platform_users._run_platform_user_lifecycle_operation(
                operation="suspend",
                organization_id=ORG_A,
                platform_user_id=USER_A,
                caller=_caller(),
                db=MagicMock(),
            )
    finally:
        platform_users.PlatformUserService = original


def test_gate_cross_organization_caller_is_not_normalized_in_router(
    monkeypatch,
):
    service = _mock_service(monkeypatch)
    caller = _caller(
        organization_id=ORG_B,
        platform_user_id=ADMIN_A,
    )
    service.suspend.side_effect = PlatformUserOrganizationBoundaryError(
        "cross-tenant caller"
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.suspend_platform_user(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            caller=caller,
            db=MagicMock(),
        )

    kwargs = service.suspend.call_args.kwargs
    assert kwargs["trusted_caller"] is caller
    assert kwargs["organization_id"] == ORG_A
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_gate_operation_selector_is_internal_only():
    for function_name in (
        "suspend_platform_user",
        "reactivate_platform_user",
        "disable_platform_user",
    ):
        signature = inspect.signature(
            getattr(platform_users, function_name)
        )
        assert "operation" not in signature.parameters
