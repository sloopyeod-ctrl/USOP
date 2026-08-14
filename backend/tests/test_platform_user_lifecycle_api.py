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


ORG_ID = "org-a"
USER_ID = "user-a"


def _caller():
    return SimpleNamespace(
        organization_id=ORG_ID,
        platform_user_id="admin-a",
        principal=SimpleNamespace(),
    )


@pytest.mark.parametrize(
    ("function_name", "operation_name"),
    [
        ("suspend_platform_user", "suspend"),
        ("reactivate_platform_user", "reactivate"),
        ("disable_platform_user", "disable"),
    ],
)
def test_lifecycle_endpoint_delegates_to_service(
    monkeypatch,
    function_name,
    operation_name,
):
    service = MagicMock()
    result = SimpleNamespace(id=USER_ID)
    getattr(service, operation_name).return_value = result

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        lambda db: service,
    )

    caller = _caller()
    db = MagicMock()

    response = getattr(platform_users, function_name)(
        organization_id=ORG_ID,
        platform_user_id=USER_ID,
        caller=caller,
        db=db,
    )

    assert response is result
    getattr(service, operation_name).assert_called_once_with(
        organization_id=ORG_ID,
        platform_user_id=USER_ID,
        trusted_caller=caller,
    )


@pytest.mark.parametrize(
    "function_name",
    [
        "suspend_platform_user",
        "reactivate_platform_user",
        "disable_platform_user",
    ],
)
def test_lifecycle_endpoint_uses_canonical_admin_permission(
    function_name,
):
    source = inspect.getsource(
        getattr(platform_users, function_name)
    )

    assert 'require_platform_permission(' in source
    assert '"platform-administration.manage"' in source


@pytest.mark.parametrize(
    "function_name",
    [
        "suspend_platform_user",
        "reactivate_platform_user",
        "disable_platform_user",
    ],
)
def test_lifecycle_endpoint_has_no_client_actor_or_status_operand(
    function_name,
):
    signature = inspect.signature(
        getattr(platform_users, function_name)
    )

    assert set(signature.parameters) == {
        "organization_id",
        "platform_user_id",
        "caller",
        "db",
    }
    assert isinstance(
        signature.parameters["caller"].default,
        params.Depends,
    )


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformUserOrganizationNotFoundError,
        PlatformUserNotFoundError,
        PlatformUserOrganizationBoundaryError,
    ],
)
def test_lifecycle_not_found_boundary_maps_to_404(
    monkeypatch,
    error_type,
):
    service = MagicMock()
    service.suspend.side_effect = error_type("hidden detail")

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.suspend_platform_user(
            organization_id=ORG_ID,
            platform_user_id=USER_ID,
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == (
        "Requested Platform User lifecycle target was not found."
    )
    assert "hidden detail" not in exc_info.value.detail


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformUserInvalidLifecycleTransitionError,
        PlatformUserLastEffectiveAdministratorError,
    ],
)
def test_lifecycle_conflict_maps_to_409(
    monkeypatch,
    error_type,
):
    service = MagicMock()
    service.disable.side_effect = error_type("lifecycle conflict")

    monkeypatch.setattr(
        platform_users,
        "PlatformUserService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.disable_platform_user(
            organization_id=ORG_ID,
            platform_user_id=USER_ID,
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "lifecycle conflict"


def test_lifecycle_routes_are_post_and_return_platform_user():
    expected = {
        "/api/v1/organizations/{organization_id}/platform-users/"
        "{platform_user_id}/suspend",
        "/api/v1/organizations/{organization_id}/platform-users/"
        "{platform_user_id}/reactivate",
        "/api/v1/organizations/{organization_id}/platform-users/"
        "{platform_user_id}/disable",
    }

    routes = {
        route.path: route
        for route in platform_users.router.routes
        if route.path in expected
    }

    assert set(routes) == expected

    for route in routes.values():
        assert route.methods == {"POST"}
        assert route.response_model is platform_users.PlatformUserRead
