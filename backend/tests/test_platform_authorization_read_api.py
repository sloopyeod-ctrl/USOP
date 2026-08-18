import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from app.api.v1 import platform_roles, platform_users
from app.services.platform_authorization_service import (
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationOrganizationNotActiveError,
    PlatformAuthorizationOrganizationNotFoundError,
    PlatformAuthorizationService,
    PlatformAuthorizationUserNotFoundError,
)


ORG = "org-a"
USER = "user-a"


def _caller():
    return SimpleNamespace(
        organization_id=ORG,
        platform_user_id="admin-a",
        principal=SimpleNamespace(),
    )


def test_service_lists_roles():
    service = PlatformAuthorizationService(MagicMock())
    service._resolve_actor_context = MagicMock()
    service._require_active_organization = MagicMock()
    service.platform_role_repository = MagicMock()
    expected = [SimpleNamespace(id="role-a")]
    service.platform_role_repository.list_for_organization.return_value = expected

    result = service.list_roles(
        organization_id=ORG,
        trusted_caller=_caller(),
    )

    assert result is expected
    service.platform_role_repository.list_for_organization.assert_called_once_with(ORG)


def test_service_lists_user_assignments():
    service = PlatformAuthorizationService(MagicMock())
    service._resolve_actor_context = MagicMock()
    service._require_active_organization = MagicMock()
    service._require_platform_user = MagicMock(
        return_value=SimpleNamespace(
            organization_id=ORG,
        )
    )
    service.assignment_repository = MagicMock()
    expected = [SimpleNamespace(id="assignment-a")]
    service.assignment_repository.list_for_user.return_value = expected

    result = service.list_user_role_assignments(
        organization_id=ORG,
        platform_user_id=USER,
        trusted_caller=_caller(),
    )

    assert result is expected
    service.assignment_repository.list_for_user.assert_called_once_with(
        organization_id=ORG,
        platform_user_id=USER,
    )


def test_service_rejects_cross_org_user_assignment_read():
    service = PlatformAuthorizationService(MagicMock())
    service._resolve_actor_context = MagicMock()
    service._require_active_organization = MagicMock()
    service._require_platform_user = MagicMock(
        return_value=SimpleNamespace(
            organization_id="org-b",
        )
    )
    service.assignment_repository = MagicMock()

    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        service.list_user_role_assignments(
            organization_id=ORG,
            platform_user_id=USER,
            trusted_caller=_caller(),
        )

    service.assignment_repository.list_for_user.assert_not_called()


def test_role_inventory_api_delegates(monkeypatch):
    service = MagicMock()
    expected = [SimpleNamespace(id="role-a")]
    service.list_roles.return_value = expected
    monkeypatch.setattr(
        platform_roles,
        "PlatformAuthorizationService",
        lambda db: service,
    )

    caller = _caller()
    result = platform_roles.list_platform_roles(
        organization_id=ORG,
        caller=caller,
        db=MagicMock(),
    )

    assert result is expected
    service.list_roles.assert_called_once_with(
        organization_id=ORG,
        trusted_caller=caller,
    )


def test_assignment_inventory_api_delegates(monkeypatch):
    service = MagicMock()
    expected = [SimpleNamespace(id="assignment-a")]
    service.list_user_role_assignments.return_value = expected
    monkeypatch.setattr(
        platform_users,
        "PlatformAuthorizationService",
        lambda db: service,
    )

    caller = _caller()
    result = platform_users.list_platform_user_roles(
        organization_id=ORG,
        platform_user_id=USER,
        caller=caller,
        db=MagicMock(),
    )

    assert result is expected
    service.list_user_role_assignments.assert_called_once_with(
        organization_id=ORG,
        platform_user_id=USER,
        trusted_caller=caller,
    )


def test_read_routes_use_canonical_admin_permission():
    assert '"platform-administration.manage"' in inspect.getsource(
        platform_roles.list_platform_roles
    )
    assert '"platform-administration.manage"' in inspect.getsource(
        platform_users.list_platform_user_roles
    )


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationOrganizationBoundaryError,
    ],
)
def test_role_inventory_not_found_maps_to_404(
    monkeypatch,
    error_type,
):
    service = MagicMock()
    service.list_roles.side_effect = error_type("internal")
    monkeypatch.setattr(
        platform_roles,
        "PlatformAuthorizationService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_roles.list_platform_roles(
            organization_id=ORG,
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "error_type",
    [
        PlatformAuthorizationOrganizationNotFoundError,
        PlatformAuthorizationUserNotFoundError,
        PlatformAuthorizationOrganizationBoundaryError,
    ],
)
def test_assignment_inventory_not_found_maps_to_404(
    monkeypatch,
    error_type,
):
    service = MagicMock()
    service.list_user_role_assignments.side_effect = error_type("internal")
    monkeypatch.setattr(
        platform_users,
        "PlatformAuthorizationService",
        lambda db: service,
    )

    with pytest.raises(HTTPException) as exc_info:
        platform_users.list_platform_user_roles(
            organization_id=ORG,
            platform_user_id=USER,
            caller=_caller(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_read_service_methods_do_not_mutate_or_audit():
    source = (
        inspect.getsource(
            PlatformAuthorizationService.list_roles
        )
        + inspect.getsource(
            PlatformAuthorizationService.list_user_role_assignments
        )
    )

    for forbidden in (
        "record_pending",
        ".create(",
        ".commit(",
        ".rollback(",
        "grant_permission",
        "assign_role(",
        "remove_role(",
    ):
        assert forbidden not in source
