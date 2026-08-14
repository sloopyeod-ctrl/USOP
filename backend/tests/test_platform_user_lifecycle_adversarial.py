import inspect
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_user_service import (
    PLATFORM_ADMINISTRATION_PERMISSION_KEY,
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
CANONICAL_PERMISSION = "platform-administration.manage"


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
        principal=SimpleNamespace(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id=f"subject-{user_id}",
        ),
    )


def _service(
    target,
    *,
    organization_id: str = ORG_A,
    candidates=None,
):
    db = MagicMock()
    service = PlatformUserService(db)

    service.organization_repository = MagicMock()
    service.organization_repository.get_by_id_for_update.return_value = (
        SimpleNamespace(id=organization_id)
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


def test_gate_contract_uses_exact_canonical_admin_permission():
    assert PLATFORM_ADMINISTRATION_PERMISSION_KEY == CANONICAL_PERMISSION


@pytest.mark.parametrize(
    ("operation_name", "initial_status"),
    [
        ("suspend", PlatformUserStatus.INVITED.value),
        ("suspend", PlatformUserStatus.SUSPENDED.value),
        ("suspend", PlatformUserStatus.DISABLED.value),
        ("reactivate", PlatformUserStatus.INVITED.value),
        ("reactivate", PlatformUserStatus.ACTIVE.value),
        ("reactivate", PlatformUserStatus.DISABLED.value),
        ("disable", PlatformUserStatus.DISABLED.value),
    ],
)
def test_gate_invalid_transitions_fail_closed(
    operation_name,
    initial_status,
):
    target = _user(USER_A, status=initial_status)
    service, db = _service(target)

    with pytest.raises(PlatformUserInvalidLifecycleTransitionError):
        getattr(service, operation_name)(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.audit_service.record_pending.assert_not_called()


def test_gate_cross_organization_target_is_non_adoptable():
    target = _user(USER_A, organization_id=ORG_B)
    service, db = _service(target)

    with pytest.raises(PlatformUserNotFoundError):
        service.disable(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.platform_user_repository.set_lifecycle_status.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


def test_gate_cross_organization_actor_fails_before_target_mutation():
    target = _user(USER_A)
    service, db = _service(target)

    with pytest.raises(PlatformUserOrganizationBoundaryError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(
                ADMIN_A,
                organization_id=ORG_B,
            ),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.organization_repository.get_by_id_for_update.assert_not_called()
    service.platform_user_repository.set_lifecycle_status.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


def test_gate_missing_trusted_actor_fails_closed():
    target = _user(USER_A)
    service, db = _service(target)

    with pytest.raises(PlatformUserOrganizationBoundaryError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=None,
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.audit_service.record_pending.assert_not_called()


def test_gate_last_effective_admin_cannot_be_suspended():
    target = _user(ADMIN_A)
    service, db = _service(target, candidates=[target])

    service.runtime_authorization_service.has_permission.side_effect = (
        lambda **kwargs: kwargs["platform_user_id"] == ADMIN_A
    )

    with pytest.raises(PlatformUserLastEffectiveAdministratorError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            trusted_caller=_caller(ADMIN_A),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.platform_user_repository.set_lifecycle_status.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


def test_gate_last_effective_admin_cannot_be_disabled():
    target = _user(ADMIN_A)
    service, db = _service(target, candidates=[target])

    service.runtime_authorization_service.has_permission.side_effect = (
        lambda **kwargs: kwargs["platform_user_id"] == ADMIN_A
    )

    with pytest.raises(PlatformUserLastEffectiveAdministratorError):
        service.disable(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            trusted_caller=_caller(ADMIN_A),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.platform_user_repository.set_lifecycle_status.assert_not_called()
    service.audit_service.record_pending.assert_not_called()


@pytest.mark.parametrize("operation_name", ["suspend", "disable"])
def test_gate_self_admin_mutation_allowed_only_with_alternate_admin(
    operation_name,
):
    target = _user(ADMIN_A)
    alternate = _user(ADMIN_B)
    service, db = _service(
        target,
        candidates=[target, alternate],
    )

    def has_permission(**kwargs):
        return kwargs["platform_user_id"] in {ADMIN_A, ADMIN_B}

    service.runtime_authorization_service.has_permission.side_effect = (
        has_permission
    )

    result = getattr(service, operation_name)(
        organization_id=ORG_A,
        platform_user_id=ADMIN_A,
        trusted_caller=_caller(ADMIN_A),
    )

    expected = (
        PlatformUserStatus.SUSPENDED.value
        if operation_name == "suspend"
        else PlatformUserStatus.DISABLED.value
    )

    assert result.status == expected
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_gate_alternate_admin_must_be_effective_under_runtime_semantics():
    target = _user(ADMIN_A)
    alternate = _user(ADMIN_B)
    service, db = _service(
        target,
        candidates=[target, alternate],
    )

    def has_permission(**kwargs):
        # Target is effective. Alternate exists but runtime RBAC denies it,
        # representing any ineffective chain: suspended user, inactive role,
        # expired assignment, inactive mapping, or inactive permission.
        return kwargs["platform_user_id"] == ADMIN_A

    service.runtime_authorization_service.has_permission.side_effect = (
        has_permission
    )

    with pytest.raises(PlatformUserLastEffectiveAdministratorError):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            trusted_caller=_caller(ADMIN_A),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_runtime_evaluator_is_authoritative_for_admin_definition():
    target = _user(ADMIN_A)
    alternate = _user(
        ADMIN_B,
        status=PlatformUserStatus.SUSPENDED.value,
    )
    service, _db = _service(
        target,
        candidates=[target, alternate],
    )

    calls = []

    def has_permission(**kwargs):
        calls.append(kwargs)
        return kwargs["platform_user_id"] == ADMIN_A

    service.runtime_authorization_service.has_permission.side_effect = (
        has_permission
    )

    with pytest.raises(PlatformUserLastEffectiveAdministratorError):
        service.disable(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            trusted_caller=_caller(ADMIN_A),
        )

    assert calls
    assert all(
        call["permission_key"] == CANONICAL_PERMISSION
        for call in calls
    )

    evaluated_times = {
        call["now"]
        for call in calls
    }
    assert len(evaluated_times) == 1


def test_gate_suspended_user_is_not_reclassified_as_effective_admin():
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
    db.commit.assert_called_once()


def test_gate_disabled_user_cannot_be_reactivated():
    target = _user(
        USER_A,
        status=PlatformUserStatus.DISABLED.value,
    )
    service, db = _service(target)

    with pytest.raises(PlatformUserInvalidLifecycleTransitionError):
        service.reactivate(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_public_operations_have_no_actor_spoofing_operand():
    for method_name in ("suspend", "reactivate", "disable"):
        signature = inspect.signature(
            getattr(PlatformUserService, method_name)
        )
        assert "actor" not in signature.parameters
        assert "updated_by" not in signature.parameters


def test_gate_public_operations_have_no_timestamp_spoofing_operand():
    for method_name in ("suspend", "reactivate", "disable"):
        signature = inspect.signature(
            getattr(PlatformUserService, method_name)
        )
        assert "evaluated_at" not in signature.parameters
        assert "timestamp" not in signature.parameters
        assert "now" not in signature.parameters


def test_gate_public_operations_have_no_arbitrary_status_operand():
    for method_name in ("suspend", "reactivate", "disable"):
        signature = inspect.signature(
            getattr(PlatformUserService, method_name)
        )
        assert "status" not in signature.parameters
        assert "new_status" not in signature.parameters


def test_gate_audit_actor_is_server_derived_from_platform_user_id():
    target = _user(USER_A)
    service, _db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False

    service.suspend(
        organization_id=ORG_A,
        platform_user_id=USER_A,
        trusted_caller=_caller("immutable-platform-user-id"),
    )

    audit_kwargs = service.audit_service.record_pending.call_args.kwargs
    assert audit_kwargs["actor"] == (
        "platform-user:immutable-platform-user-id"
    )
    assert audit_kwargs["metadata"]["actor_platform_user_id"] == (
        "immutable-platform-user-id"
    )
    assert audit_kwargs["metadata"]["actor_trust"] == (
        "AuthenticatedPlatformCaller"
    )


def test_gate_audit_failure_prevents_commit_and_rolls_back():
    target = _user(USER_A)
    service, db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False
    service.audit_service.record_pending.side_effect = RuntimeError(
        "adversarial audit failure"
    )

    with pytest.raises(RuntimeError, match="adversarial audit failure"):
        service.disable(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_commit_failure_rolls_back_transaction():
    target = _user(USER_A)
    service, db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False
    db.commit.side_effect = RuntimeError("commit failure")

    with pytest.raises(RuntimeError, match="commit failure"):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.rollback.assert_called_once()


def test_gate_lifecycle_repository_contract_cannot_receive_is_active():
    target = _user(USER_A, is_active=True)
    service, _db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False

    service.suspend(
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


def test_gate_detects_accidental_repository_is_active_mutation():
    target = _user(USER_A, is_active=True)
    service, db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False

    def malicious_lifecycle_mutation(
        *,
        platform_user,
        status,
        updated_by,
    ):
        platform_user.status = status
        platform_user.updated_by = updated_by
        platform_user.is_active = False
        return platform_user

    service.platform_user_repository.set_lifecycle_status.side_effect = (
        malicious_lifecycle_mutation
    )

    with pytest.raises(
        ValueError,
        match="record lifecycle state",
    ):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.audit_service.record_pending.assert_not_called()


def test_gate_organization_lock_precedes_lifecycle_mutation():
    target = _user(USER_A)
    service, _db = _service(target)
    service.runtime_authorization_service.has_permission.return_value = False

    events = []

    service.organization_repository.get_by_id_for_update.side_effect = (
        lambda organization_id: (
            events.append("organization_lock")
            or SimpleNamespace(id=organization_id)
        )
    )

    def set_lifecycle_status(*, platform_user, status, updated_by):
        events.append("lifecycle_mutation")
        platform_user.status = status
        platform_user.updated_by = updated_by
        return platform_user

    service.platform_user_repository.set_lifecycle_status.side_effect = (
        set_lifecycle_status
    )

    service.suspend(
        organization_id=ORG_A,
        platform_user_id=USER_A,
        trusted_caller=_caller(),
    )

    assert events.index("organization_lock") < events.index(
        "lifecycle_mutation"
    )


def test_gate_unknown_organization_fails_before_target_mutation():
    target = _user(USER_A)
    service, db = _service(target)
    service.organization_repository.get_by_id_for_update.return_value = None

    with pytest.raises(ValueError, match="unknown Organization"):
        service.suspend(
            organization_id=ORG_A,
            platform_user_id=USER_A,
            trusted_caller=_caller(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.platform_user_repository.set_lifecycle_status.assert_not_called()
    service.audit_service.record_pending.assert_not_called()
