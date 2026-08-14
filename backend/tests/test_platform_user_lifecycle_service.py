from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_user_service import (
    PlatformUserInvalidLifecycleTransitionError,
    PlatformUserLastEffectiveAdministratorError,
    PlatformUserNotFoundError,
    PlatformUserOrganizationBoundaryError,
    PlatformUserService,
)


ORG_A = "org-a"
ORG_B = "org-b"
ADMIN_A = "admin-a"
ADMIN_B = "admin-b"
USER_A = "user-a"


def _user(
    user_id: str,
    *,
    organization_id: str = ORG_A,
    status: str = PlatformUserStatus.ACTIVE.value,
    is_active: bool = True,
):
    return SimpleNamespace(
        id=user_id,
        organization_id=organization_id,
        display_name=user_id,
        status=status,
        is_active=is_active,
        updated_by=None,
    )


def _caller(
    user_id: str = ADMIN_A,
    *,
    organization_id: str = ORG_A,
):
    return SimpleNamespace(
        organization_id=organization_id,
        platform_user_id=user_id,
        principal=SimpleNamespace(),
    )


def _service(target, *, candidates=None):
    db = MagicMock()
    service = PlatformUserService(db)

    service.organization_repository = MagicMock()
    service.organization_repository.get_by_id_for_update.return_value = (
        SimpleNamespace(id=ORG_A)
    )

    service.platform_user_repository = MagicMock()
    service.platform_user_repository.get_by_id.return_value = target
    service.platform_user_repository.list_for_organization.return_value = (
        candidates if candidates is not None else [target]
    )

    def set_lifecycle_status(*, platform_user, status, updated_by):
        platform_user.status = status
        platform_user.updated_by = updated_by
        return platform_user

    service.platform_user_repository.set_lifecycle_status.side_effect = (
        set_lifecycle_status
    )

    service.runtime_authorization_service = MagicMock()
    service.audit_service = MagicMock()
    service.audit_service.record_pending.return_value = SimpleNamespace(
        id="audit-1"
    )

    return service, db


def test_suspend_active_user_preserves_record_lifecycle_and_audits():
    target = _user(USER_A)
    service, db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False

    result = service.suspend(
        organization_id=ORG_A,
        platform_user_id=USER_A,
        trusted_caller=_caller(),
    )

    assert result.status == PlatformUserStatus.SUSPENDED.value
    assert result.is_active is True
    assert result.updated_by == "platform-user:admin-a"
    db.commit.assert_called_once()
    db.rollback.assert_not_called()

    audit_kwargs = service.audit_service.record_pending.call_args.kwargs
    assert audit_kwargs["event_type"] == "PlatformUserSuspended"
    assert audit_kwargs["actor"] == "platform-user:admin-a"
    assert audit_kwargs["metadata"]["previous_status"] == "Active"
    assert audit_kwargs["metadata"]["new_status"] == "Suspended"
    assert audit_kwargs["metadata"]["is_active_preserved"] is True


def test_reactivate_only_accepts_suspended():
    target = _user(USER_A)
    service, db = _service(target)

    with pytest.raises(PlatformUserInvalidLifecycleTransitionError):
        service.reactivate(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_disabled_is_terminal_for_reactivation():
    target = _user(
        USER_A,
        status=PlatformUserStatus.DISABLED.value,
    )
    service, _db = _service(target)

    with pytest.raises(PlatformUserInvalidLifecycleTransitionError):
        service.reactivate(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )


def test_cross_organization_target_is_not_found():
    target = _user(USER_A, organization_id=ORG_B)
    service, _db = _service(target)

    with pytest.raises(PlatformUserNotFoundError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )


def test_cross_organization_trusted_actor_fails_closed():
    target = _user(USER_A)
    service, _db = _service(target)

    with pytest.raises(PlatformUserOrganizationBoundaryError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(organization_id=ORG_B),
        )


def test_only_effective_admin_cannot_self_suspend():
    target = _user(ADMIN_A)
    service, db = _service(target, candidates=[target])
    service.runtime_authorization_service.has_permission.return_value = True

    with pytest.raises(PlatformUserLastEffectiveAdministratorError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            trusted_caller=_caller(ADMIN_A),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_self_suspend_allowed_when_another_effective_admin_remains():
    target = _user(ADMIN_A)
    alternate = _user(ADMIN_B)
    service, db = _service(target, candidates=[target, alternate])

    def has_permission(**kwargs):
        return kwargs["platform_user_id"] in {ADMIN_A, ADMIN_B}

    service.runtime_authorization_service.has_permission.side_effect = (
        has_permission
    )

    result = service.suspend(
        organization_id=ORG_A,
        platform_user_id=ADMIN_A,
        trusted_caller=_caller(ADMIN_A),
    )

    assert result.status == PlatformUserStatus.SUSPENDED.value
    db.commit.assert_called_once()


def test_only_effective_admin_cannot_be_disabled():
    target = _user(ADMIN_A)
    service, db = _service(target, candidates=[target])
    service.runtime_authorization_service.has_permission.return_value = True

    with pytest.raises(PlatformUserLastEffectiveAdministratorError):
        service.disable(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            trusted_caller=_caller(ADMIN_A),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_suspended_user_can_be_disabled_without_false_last_admin_block():
    target = _user(
        ADMIN_A,
        status=PlatformUserStatus.SUSPENDED.value,
    )
    service, db = _service(target, candidates=[target])
    service.runtime_authorization_service.has_permission.return_value = False

    result = service.disable(
        organization_id=ORG_A,
        platform_user_id=ADMIN_A,
        trusted_caller=_caller(ADMIN_B),
    )

    assert result.status == PlatformUserStatus.DISABLED.value
    assert result.is_active is True
    db.commit.assert_called_once()


def test_audit_failure_rolls_back_lifecycle_transaction():
    target = _user(USER_A)
    service, db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False
    service.audit_service.record_pending.side_effect = RuntimeError(
        "audit failure"
    )

    with pytest.raises(RuntimeError, match="audit failure"):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_repository_contract_has_no_is_active_lifecycle_operand():
    target = _user(USER_A, is_active=True)
    service, _db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False

    service.disable(
        organization_id=ORG_A,
        platform_user_id=USER_A,
        trusted_caller=_caller(),
    )

    kwargs = (
        service.platform_user_repository
        .set_lifecycle_status
        .call_args
        .kwargs
    )

    assert set(kwargs) == {
        "platform_user",
        "status",
        "updated_by",
    }
    assert target.is_active is True
