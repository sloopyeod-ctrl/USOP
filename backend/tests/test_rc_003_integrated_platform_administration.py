from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.domain.organization_status import OrganizationStatus
from app.domain.platform_role_status import PlatformRoleStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.models.platform_role_assignment import PlatformRoleAssignment
from app.services.platform_authorization_service import (
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationService,
)
from app.services.platform_runtime_authorization_result import (
    PlatformRuntimeAuthorizationDisposition,
)
from app.services.platform_runtime_authorization_service import (
    PlatformRuntimeAuthorizationService,
)
from app.services.platform_user_service import (
    PLATFORM_ADMINISTRATION_PERMISSION_KEY,
    PlatformUserLastEffectiveAdministratorError,
    PlatformUserService,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG_A = "org-a"
ORG_B = "org-b"
ADMIN_A = "admin-a"
INVITED_B = "invited-b"
ADMIN_ROLE = "role-admin"
ADMIN_PERMISSION = "permission-admin"
NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)


def _caller(user_id=ADMIN_A, *, organization_id=ORG_A):
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id=user_id,
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id=f"subject-{user_id}",
        ),
    )


def _user(
    user_id,
    *,
    organization_id=ORG_A,
    status=PlatformUserStatus.ACTIVE.value,
):
    return SimpleNamespace(
        id=user_id,
        organization_id=organization_id,
        display_name=user_id,
        email=f"{user_id}@example.com",
        status=status,
        is_active=True,
        updated_by=None,
        created_via_bootstrap=False,
        organizational_identity_id=None,
    )


def _role():
    return SimpleNamespace(
        id=ADMIN_ROLE,
        organization_id=ORG_A,
        name="Platform Administrator",
        role_key="platform-administrator",
        status=PlatformRoleStatus.ACTIVE.value,
        is_active=True,
    )


def _permission():
    return SimpleNamespace(
        id=ADMIN_PERMISSION,
        permission_key=PLATFORM_ADMINISTRATION_PERMISSION_KEY,
        resource="platform-administration",
        action="manage",
        is_active=True,
    )


class InMemoryPlatformUserRepository:
    def __init__(self, users=None):
        self.users = {user.id: user for user in (users or [])}
        self.db = None

    def get_by_id(self, platform_user_id):
        return self.users.get(platform_user_id)

    def get_by_external_identity(
        self,
        *,
        organization_id,
        identity_provider,
        external_tenant_id,
        external_subject_id,
    ):
        for user in self.users.values():
            if (
                user.organization_id == organization_id
                and getattr(user, "identity_provider", None)
                == identity_provider
                and getattr(user, "external_tenant_id", None)
                == external_tenant_id
                and getattr(user, "external_subject_id", None)
                == external_subject_id
            ):
                return user
        return None

    def create(self, platform_user):
        if not getattr(platform_user, "id", None):
            platform_user.id = INVITED_B

        if getattr(platform_user, "is_active", None) is None:
            platform_user.is_active = True

        self.users[platform_user.id] = platform_user
        return platform_user

    def list_for_organization(self, organization_id):
        return [
            user
            for user in self.users.values()
            if user.organization_id == organization_id
        ]

    def set_lifecycle_status(
        self,
        *,
        platform_user,
        status,
        updated_by,
    ):
        previous_status = platform_user.status
        previous_updated_by = platform_user.updated_by

        if self.db is not None:
            self.db.add_undo(
                lambda: self._restore_lifecycle(
                    platform_user,
                    previous_status,
                    previous_updated_by,
                )
            )

        platform_user.status = status
        platform_user.updated_by = updated_by
        return platform_user

    @staticmethod
    def _restore_lifecycle(
        platform_user,
        status,
        updated_by,
    ):
        platform_user.status = status
        platform_user.updated_by = updated_by


class InMemoryAssignmentRepository:
    def __init__(self):
        self.assignments = {}
        self.db = None

    @staticmethod
    def _key(
        organization_id,
        platform_user_id,
        platform_role_id,
    ):
        return (
            organization_id,
            platform_user_id,
            platform_role_id,
        )

    def create(self, assignment):
        if not getattr(assignment, "id", None):
            assignment.id = (
                f"assignment-{assignment.platform_user_id}-"
                f"{assignment.platform_role_id}"
            )

        if getattr(assignment, "is_active", None) is None:
            assignment.is_active = True

        key = self._key(
            assignment.organization_id,
            assignment.platform_user_id,
            assignment.platform_role_id,
        )

        previous = self.assignments.get(key)

        if self.db is not None:
            if previous is None:
                self.db.add_undo(
                    lambda: self.assignments.pop(key, None)
                )
            else:
                self.db.add_undo(
                    lambda: self.assignments.__setitem__(
                        key,
                        previous,
                    )
                )

        self.assignments[key] = assignment
        return assignment

    def get_assignment(
        self,
        *,
        organization_id,
        platform_user_id,
        platform_role_id,
    ):
        return self.assignments.get(
            self._key(
                organization_id,
                platform_user_id,
                platform_role_id,
            )
        )

    def list_for_user(
        self,
        *,
        organization_id,
        platform_user_id,
    ):
        return [
            assignment
            for assignment in self.assignments.values()
            if (
                assignment.organization_id == organization_id
                and assignment.platform_user_id == platform_user_id
            )
        ]

    def delete_object(self, assignment):
        key = self._key(
            assignment.organization_id,
            assignment.platform_user_id,
            assignment.platform_role_id,
        )

        previous = self.assignments.get(key)

        if self.db is not None and previous is not None:
            self.db.add_undo(
                lambda: self.assignments.__setitem__(
                    key,
                    previous,
                )
            )

        self.assignments.pop(key, None)


class IntegratedDb:
    def __init__(self, assignment_repository):
        self.assignment_repository = assignment_repository
        self.commit_count = 0
        self.rollback_count = 0
        self._undo_actions = []

    def add_undo(self, action):
        self._undo_actions.append(action)

    def add(self, value):
        return None

    def flush(self):
        return None

    def refresh(self, value):
        return None

    def commit(self):
        self.commit_count += 1
        self._undo_actions.clear()

    def rollback(self):
        self.rollback_count += 1

        for action in reversed(self._undo_actions):
            action()

        self._undo_actions.clear()

    def delete(self, value):
        if isinstance(value, PlatformRoleAssignment):
            self.assignment_repository.delete_object(value)


class IntegratedHarness:
    def __init__(self):
        self.admin_a = _user(ADMIN_A)
        self.users = InMemoryPlatformUserRepository([self.admin_a])
        self.assignments = InMemoryAssignmentRepository()
        self.db = IntegratedDb(self.assignments)

        self.users.db = self.db
        self.assignments.db = self.db

        self.organization = SimpleNamespace(
            id=ORG_A,
            status=OrganizationStatus.ACTIVE.value,
        )
        self.role = _role()
        self.permission = _permission()
        self.mapping = SimpleNamespace(
            id="mapping-admin",
            organization_id=ORG_A,
            platform_role_id=ADMIN_ROLE,
            platform_permission_id=ADMIN_PERMISSION,
            is_active=True,
        )

        self.organization_repository = MagicMock()
        self.organization_repository.get_by_id_for_update.return_value = (
            self.organization
        )
        self.organization_repository.get_by_id.return_value = (
            self.organization
        )

        self.role_repository = MagicMock()
        self.role_repository.get_by_id.return_value = self.role

        self.permission_repository = MagicMock()
        self.permission_repository.get_by_key.return_value = self.permission

        self.mapping_repository = MagicMock()
        self.mapping_repository.list_for_role.return_value = [self.mapping]

        self.audit_service = MagicMock()
        self.audit_service.record_pending.side_effect = (
            lambda **kwargs: SimpleNamespace(
                id=f"audit-{self.audit_service.record_pending.call_count}"
            )
        )

        self.runtime = PlatformRuntimeAuthorizationService(
            self.db,
            platform_user_repository=self.users,
            platform_role_assignment_repository=self.assignments,
            platform_role_repository=self.role_repository,
            platform_role_permission_repository=self.mapping_repository,
            platform_permission_repository=self.permission_repository,
        )

        self.user_service = PlatformUserService(self.db)
        self.user_service.organization_repository = self.organization_repository
        self.user_service.platform_user_repository = self.users
        self.user_service.runtime_authorization_service = self.runtime
        self.user_service.audit_service = self.audit_service

        self.authorization_service = PlatformAuthorizationService(self.db)
        self.authorization_service.organization_repository = (
            self.organization_repository
        )
        self.authorization_service.platform_user_repository = self.users
        self.authorization_service.platform_role_repository = (
            self.role_repository
        )
        self.authorization_service.platform_permission_repository = (
            self.permission_repository
        )
        self.authorization_service.assignment_repository = self.assignments
        self.authorization_service.mapping_repository = self.mapping_repository
        self.authorization_service.audit_service = self.audit_service

    def invite_b(self):
        return self.user_service.invite(
            organization_id=ORG_A,
            display_name="User B",
            email="user-b@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-user-b",
            trusted_caller=_caller(),
        )

    def activate(self, user):
        user.status = PlatformUserStatus.ACTIVE.value
        user.is_active = True

    def assign_admin(self, user):
        return self.authorization_service.assign_role(
            organization_id=ORG_A,
            platform_user_id=user.id,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
            trusted_caller=_caller(),
        )

    def remove_admin(self, user):
        return self.authorization_service.remove_role(
            organization_id=ORG_A,
            platform_user_id=user.id,
            platform_role_id=ADMIN_ROLE,
            trusted_caller=_caller(),
        )

    def has_admin(self, user):
        return self.runtime.has_permission(
            organization_id=ORG_A,
            platform_user_id=user.id,
            permission_key=PLATFORM_ADMINISTRATION_PERMISSION_KEY,
            now=NOW,
        )


def test_integrated_invite_assign_activate_remove_authority_chain():
    harness = IntegratedHarness()
    invited = harness.invite_b()

    assert invited.status == PlatformUserStatus.INVITED.value
    assert harness.has_admin(invited) is False

    harness.assign_admin(invited)
    assert harness.has_admin(invited) is False

    harness.activate(invited)
    assert harness.has_admin(invited) is True

    harness.remove_admin(invited)
    assert harness.has_admin(invited) is False


def test_integrated_suspension_immediately_removes_runtime_authority():
    harness = IntegratedHarness()
    admin_b = harness.invite_b()
    harness.assign_admin(admin_b)
    harness.activate(admin_b)

    harness.assignments.create(
        PlatformRoleAssignment(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
        )
    )

    assert harness.has_admin(harness.admin_a) is True
    assert harness.has_admin(admin_b) is True

    harness.user_service.suspend(
        organization_id=ORG_A,
        platform_user_id=admin_b.id,
        trusted_caller=_caller(),
    )

    assert admin_b.status == PlatformUserStatus.SUSPENDED.value
    assert harness.has_admin(admin_b) is False
    assert harness.has_admin(harness.admin_a) is True


def test_integrated_last_effective_admin_is_protected_after_peer_suspension():
    harness = IntegratedHarness()
    admin_b = harness.invite_b()
    harness.assign_admin(admin_b)
    harness.activate(admin_b)

    harness.assignments.create(
        PlatformRoleAssignment(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
        )
    )

    assert harness.has_admin(harness.admin_a) is True
    assert harness.has_admin(admin_b) is True

    harness.user_service.suspend(
        organization_id=ORG_A,
        platform_user_id=ADMIN_A,
        trusted_caller=_caller(ADMIN_A),
    )

    assert harness.has_admin(harness.admin_a) is False
    assert harness.has_admin(admin_b) is True

    with pytest.raises(
        PlatformUserLastEffectiveAdministratorError
    ):
        harness.user_service.disable(
            organization_id=ORG_A,
            platform_user_id=admin_b.id,
            trusted_caller=_caller(admin_b.id),
        )

    assert admin_b.status == PlatformUserStatus.ACTIVE.value
    assert harness.has_admin(admin_b) is True


def test_integrated_cross_org_assignment_fails_before_authority_change():
    harness = IntegratedHarness()
    foreign_user = _user(
        "foreign-user",
        organization_id=ORG_B,
    )
    harness.users.users[foreign_user.id] = foreign_user

    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        harness.authorization_service.assign_role(
            organization_id=ORG_A,
            platform_user_id=foreign_user.id,
            platform_role_id=ADMIN_ROLE,
            trusted_caller=_caller(),
        )

    assert harness.has_admin(foreign_user) is False
    assert (
        harness.assignments.list_for_user(
            organization_id=ORG_A,
            platform_user_id=foreign_user.id,
        )
        == []
    )


def test_integrated_runtime_evaluator_remains_authoritative():
    harness = IntegratedHarness()
    invited = harness.invite_b()
    harness.assign_admin(invited)

    result = harness.runtime.evaluate(
        organization_id=ORG_A,
        platform_user_id=invited.id,
        permission_key=PLATFORM_ADMINISTRATION_PERMISSION_KEY,
        now=NOW,
    )

    assert result.disposition == PlatformRuntimeAuthorizationDisposition.DENY
    assert result.reason == "PlatformUserNotActive"

    harness.activate(invited)

    result = harness.runtime.evaluate(
        organization_id=ORG_A,
        platform_user_id=invited.id,
        permission_key=PLATFORM_ADMINISTRATION_PERMISSION_KEY,
        now=NOW,
    )

    assert result.disposition == PlatformRuntimeAuthorizationDisposition.ALLOW
    assert result.reason == "PermissionGrantedByActiveRole"


def test_integrated_assignment_audit_failure_rolls_back_and_grants_no_authority():
    harness = IntegratedHarness()
    invited = harness.invite_b()
    harness.activate(invited)

    original_record_pending = harness.audit_service.record_pending.side_effect

    def fail_assignment_audit(**kwargs):
        if kwargs.get("event_type") == "PlatformRoleAssigned":
            raise RuntimeError("assignment audit unavailable")
        return original_record_pending(**kwargs)

    harness.audit_service.record_pending.side_effect = fail_assignment_audit

    with pytest.raises(
        RuntimeError,
        match="assignment audit unavailable",
    ):
        harness.authorization_service.assign_role(
            organization_id=ORG_A,
            platform_user_id=invited.id,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
            trusted_caller=_caller(),
        )

    assert harness.db.rollback_count >= 1
    assert harness.has_admin(invited) is False


def test_integrated_assignment_commit_failure_rolls_back_and_grants_no_authority():
    harness = IntegratedHarness()
    invited = harness.invite_b()
    harness.activate(invited)

    original_commit = harness.db.commit

    def fail_commit():
        raise RuntimeError("assignment commit failed")

    harness.db.commit = fail_commit

    with pytest.raises(
        RuntimeError,
        match="assignment commit failed",
    ):
        harness.authorization_service.assign_role(
            organization_id=ORG_A,
            platform_user_id=invited.id,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
            trusted_caller=_caller(),
        )

    harness.db.commit = original_commit

    assert harness.db.rollback_count >= 1
    assert harness.has_admin(invited) is False


def test_integrated_role_removal_audit_failure_rolls_back_transaction():
    harness = IntegratedHarness()
    invited = harness.invite_b()
    harness.assign_admin(invited)
    harness.activate(invited)

    assert harness.has_admin(invited) is True

    original_record_pending = harness.audit_service.record_pending.side_effect

    def fail_removal_audit(**kwargs):
        if kwargs.get("event_type") == "PlatformRoleRemoved":
            raise RuntimeError("removal audit unavailable")
        return original_record_pending(**kwargs)

    harness.audit_service.record_pending.side_effect = fail_removal_audit

    with pytest.raises(
        RuntimeError,
        match="removal audit unavailable",
    ):
        harness.authorization_service.remove_role(
            organization_id=ORG_A,
            platform_user_id=invited.id,
            platform_role_id=ADMIN_ROLE,
            trusted_caller=_caller(),
        )

    assert harness.db.rollback_count >= 1
    assert harness.has_admin(invited) is True


def test_integrated_lifecycle_audit_failure_preserves_authority_and_status():
    harness = IntegratedHarness()
    admin_b = harness.invite_b()
    harness.assign_admin(admin_b)
    harness.activate(admin_b)

    harness.assignments.create(
        PlatformRoleAssignment(
            organization_id=ORG_A,
            platform_user_id=ADMIN_A,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
        )
    )

    assert harness.has_admin(admin_b) is True
    assert harness.has_admin(harness.admin_a) is True

    original_status = admin_b.status
    original_record_pending = harness.audit_service.record_pending.side_effect

    def fail_suspend_audit(**kwargs):
        if kwargs.get("event_type") == "PlatformUserSuspended":
            raise RuntimeError("lifecycle audit unavailable")
        return original_record_pending(**kwargs)

    harness.audit_service.record_pending.side_effect = fail_suspend_audit

    with pytest.raises(
        RuntimeError,
        match="lifecycle audit unavailable",
    ):
        harness.user_service.suspend(
            organization_id=ORG_A,
            platform_user_id=admin_b.id,
            trusted_caller=_caller(),
        )

    assert harness.db.rollback_count >= 1
    assert admin_b.status == original_status
    assert harness.has_admin(admin_b) is True


def test_integrated_cross_org_trusted_caller_cannot_mutate_authority():
    harness = IntegratedHarness()
    invited = harness.invite_b()
    harness.activate(invited)

    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        harness.authorization_service.assign_role(
            organization_id=ORG_A,
            platform_user_id=invited.id,
            platform_role_id=ADMIN_ROLE,
            assigned_at=NOW,
            trusted_caller=_caller(
                organization_id=ORG_B,
            ),
        )

    assert harness.has_admin(invited) is False
