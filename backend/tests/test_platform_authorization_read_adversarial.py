import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, params, status

from app.api.v1 import platform_roles, platform_users
from app.schemas.platform_role import PlatformRoleRead
from app.schemas.platform_role_assignment import (
    PlatformRoleAssignmentRead,
)
from app.services.platform_authorization_service import (
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationOrganizationNotActiveError,
    PlatformAuthorizationOrganizationNotFoundError,
    PlatformAuthorizationService,
    PlatformAuthorizationUserNotFoundError,
)


ORG_A = "org-a"
ORG_B = "org-b"
USER_A = "user-a"


def _caller(
    *,
    organization_id: str = ORG_A,
    platform_user_id: str = "admin-a",
):
    return SimpleNamespace(
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        principal=SimpleNamespace(),
    )


def _service(monkeypatch, module):
    service = MagicMock()
    monkeypatch.setattr(
        module,
        "PlatformAuthorizationService",
        lambda db: service,
    )
    return service


def test_gate_role_inventory_route_is_get_only():
    matches = [
        route
        for route in platform_roles.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/platform-roles/"
        )
    ]

    assert len(matches) == 1
    assert matches[0].methods == {"GET"}
    assert matches[0].response_model == list[PlatformRoleRead]


def test_gate_user_assignment_inventory_route_is_get_only():
    matches = [
        route
        for route in platform_users.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/platform-users/"
            "{platform_user_id}/roles"
        )
        and route.methods == {"GET"}
    ]

    assert len(matches) == 1
    assert matches[0].response_model == list[
        PlatformRoleAssignmentRead
    ]


def test_gate_read_routes_require_server_managed_caller():
    role_signature = inspect.signature(
        platform_roles.list_platform_roles
    )
    assignment_signature = inspect.signature(
        platform_users.list_platform_user_roles
    )

    assert isinstance(
        role_signature.parameters["caller"].default,
        params.Depends,
    )
    assert isinstance(
        assignment_signature.parameters["caller"].default,
        params.Depends,
    )


def test_gate_read_routes_use_exact_canonical_permission():
    role_source = inspect.getsource(
        platform_roles.list_platform_roles
    )
    assignment_source = inspect.getsource(
        platform_users.list_platform_user_roles
    )

    assert role_source.count(
        '"platform-administration.manage"'
    ) == 1
    assert assignment_source.count(
        '"platform-administration.manage"'
    ) == 1


def test_gate_role_inventory_passes_trusted_caller_unchanged(
    monkeypatch,
):
    service = _service(
        monkeypatch,
        platform_roles,
    )
    caller = _caller()
    service.list_roles.return_value = []

    platform_roles.list_platform_roles(
        organization_id=ORG_A,
        caller=caller,
        db=MagicMock(),
    )

    kwargs = service.list_roles.call_args.kwargs
    assert kwargs["trusted_caller"] is caller
    assert kwargs["organization_id"] == ORG_A


def test_gate_assignment_inventory_passes_trusted_caller_unchanged(
    monkeypatch,
):
    service = _service(
        monkeypatch,
        platform_users,
    )
    caller = _caller()
    service.list_user_role_assignments.return_value = []

    platform_users.list_platform_user_roles(
        organization_id=ORG_A,
        platform_user_id=USER_A,
        caller=caller,
        db=MagicMock(),
    )

    kwargs = (
        service
        .list_user_role_assignments
        .call_args
        .kwargs
    )
    assert kwargs["trusted_caller"] is caller
    assert kwargs["organization_id"] == ORG_A
    assert kwargs["platform_user_id"] == USER_A


def test_gate_cross_org_caller_is_not_normalized_in_router(
    monkeypatch,
):
    service = _service(
        monkeypatch,
        platform_roles,
    )
    caller = _caller(
        organization_id=ORG_B,
    )
    service.list_roles.side_effect = (
        PlatformAuthorizationOrganizationBoundaryError(
            "cross-org caller"
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_roles.list_platform_roles(
            organization_id=ORG_A,
            caller=caller,
            db=MagicMock(),
        )

    kwargs = service.list_roles.call_args.kwargs
    assert kwargs["trusted_caller"] is caller
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_gate_service_role_read_validates_caller_before_repository():
    service = PlatformAuthorizationService(MagicMock())
    service._resolve_actor_context = MagicMock(
        side_effect=PlatformAuthorizationOrganizationBoundaryError(
            "caller mismatch"
        )
    )
    service._require_active_organization = MagicMock()
    service.platform_role_repository = MagicMock()

    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        service.list_roles(
            organization_id=ORG_A,
            trusted_caller=_caller(
                organization_id=ORG_B,
            ),
        )

    service._require_active_organization.assert_not_called()
    service.platform_role_repository.list_for_organization.assert_not_called()


def test_gate_service_assignment_read_validates_caller_before_user_lookup():
    service = PlatformAuthorizationService(MagicMock())
    service._resolve_actor_context = MagicMock(
        side_effect=PlatformAuthorizationOrganizationBoundaryError(
            "caller mismatch"
        )
    )
    service._require_active_organization = MagicMock()
    service._require_platform_user = MagicMock()
    service.assignment_repository = MagicMock()

    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        service.list_user_role_assignments(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(
                organization_id=ORG_B,
            ),
        )

    service._require_active_organization.assert_not_called()
    service._require_platform_user.assert_not_called()
    service.assignment_repository.list_for_user.assert_not_called()


def test_gate_assignment_read_blocks_cross_org_user_before_repository():
    service = PlatformAuthorizationService(MagicMock())
    service._resolve_actor_context = MagicMock()
    service._require_active_organization = MagicMock()
    service._require_platform_user = MagicMock(
        return_value=SimpleNamespace(
            organization_id=ORG_B,
        )
    )
    service.assignment_repository = MagicMock()

    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        service.list_user_role_assignments(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    service.assignment_repository.list_for_user.assert_not_called()


@pytest.mark.parametrize(
    ("module", "function_name", "service_method", "error_type"),
    [
        (
            platform_roles,
            "list_platform_roles",
            "list_roles",
            PlatformAuthorizationOrganizationNotFoundError,
        ),
        (
            platform_roles,
            "list_platform_roles",
            "list_roles",
            PlatformAuthorizationOrganizationBoundaryError,
        ),
        (
            platform_users,
            "list_platform_user_roles",
            "list_user_role_assignments",
            PlatformAuthorizationOrganizationNotFoundError,
        ),
        (
            platform_users,
            "list_platform_user_roles",
            "list_user_role_assignments",
            PlatformAuthorizationUserNotFoundError,
        ),
        (
            platform_users,
            "list_platform_user_roles",
            "list_user_role_assignments",
            PlatformAuthorizationOrganizationBoundaryError,
        ),
    ],
)
def test_gate_not_found_errors_are_uniform_and_non_leaking(
    monkeypatch,
    module,
    function_name,
    service_method,
    error_type,
):
    service = _service(
        monkeypatch,
        module,
    )
    getattr(
        service,
        service_method,
    ).side_effect = error_type(
        "tenant-sensitive internal detail"
    )

    function = getattr(
        module,
        function_name,
    )

    kwargs = {
        "organization_id": ORG_A,
        "caller": _caller(),
        "db": MagicMock(),
    }

    if function_name == "list_platform_user_roles":
        kwargs["platform_user_id"] = USER_A

    with pytest.raises(HTTPException) as exc_info:
        function(**kwargs)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == (
        "Requested Platform authorization target was not found."
    )
    assert "tenant-sensitive" not in exc_info.value.detail


@pytest.mark.parametrize(
    ("module", "function_name", "service_method"),
    [
        (
            platform_roles,
            "list_platform_roles",
            "list_roles",
        ),
        (
            platform_users,
            "list_platform_user_roles",
            "list_user_role_assignments",
        ),
    ],
)
def test_gate_inactive_org_never_becomes_success(
    monkeypatch,
    module,
    function_name,
    service_method,
):
    service = _service(
        monkeypatch,
        module,
    )
    getattr(
        service,
        service_method,
    ).side_effect = (
        PlatformAuthorizationOrganizationNotActiveError(
            "inactive"
        )
    )

    function = getattr(
        module,
        function_name,
    )

    kwargs = {
        "organization_id": ORG_A,
        "caller": _caller(),
        "db": MagicMock(),
    }

    if function_name == "list_platform_user_roles":
        kwargs["platform_user_id"] = USER_A

    with pytest.raises(HTTPException) as exc_info:
        function(**kwargs)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_gate_unexpected_internal_failure_is_not_reclassified_role(
    monkeypatch,
):
    service = _service(
        monkeypatch,
        platform_roles,
    )
    service.list_roles.side_effect = RuntimeError(
        "unexpected"
    )

    with pytest.raises(
        RuntimeError,
        match="unexpected",
    ):
        platform_roles.list_platform_roles(
            organization_id=ORG_A,
            caller=_caller(),
            db=MagicMock(),
        )


def test_gate_unexpected_internal_failure_is_not_reclassified_assignment(
    monkeypatch,
):
    service = _service(
        monkeypatch,
        platform_users,
    )
    service.list_user_role_assignments.side_effect = RuntimeError(
        "unexpected"
    )

    with pytest.raises(
        RuntimeError,
        match="unexpected",
    ):
        platform_users.list_platform_user_roles(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            caller=_caller(),
            db=MagicMock(),
        )


def test_gate_service_read_methods_are_side_effect_free():
    source = (
        inspect.getsource(
            PlatformAuthorizationService.list_roles
        )
        + inspect.getsource(
            PlatformAuthorizationService.list_user_role_assignments
        )
    )

    forbidden = (
        ".create(",
        ".commit(",
        ".rollback(",
        "record_pending",
        "assign_role(",
        "remove_role(",
        "grant_permission(",
        "remove_permission(",
        "AuditService(",
    )

    for fragment in forbidden:
        assert fragment not in source


def test_gate_read_routes_have_no_body_models():
    role_route = next(
        route
        for route in platform_roles.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/platform-roles/"
        )
        and route.methods == {"GET"}
    )
    assignment_route = next(
        route
        for route in platform_users.router.routes
        if route.path == (
            "/api/v1/organizations/{organization_id}/platform-users/"
            "{platform_user_id}/roles"
        )
        and route.methods == {"GET"}
    )

    assert role_route.dependant.body_params == []
    assert assignment_route.dependant.body_params == []


def test_gate_read_routes_do_not_duplicate_authorization_policy():
    source = (
        inspect.getsource(
            platform_roles.list_platform_roles
        )
        + inspect.getsource(
            platform_users.list_platform_user_roles
        )
    )

    forbidden = (
        "PlatformRoleStatus.",
        "PlatformUserStatus.",
        "organization_id ==",
        "organization_id !=",
        "is_active",
        "expires_at",
        "has_permission(",
        "PlatformRuntimeAuthorizationService",
    )

    for fragment in forbidden:
        assert fragment not in source
