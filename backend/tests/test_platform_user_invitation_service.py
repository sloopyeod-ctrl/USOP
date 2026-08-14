from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.organization_status import OrganizationStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_user_service import (
    PlatformUserExternalIdentityConflictError,
    PlatformUserInvitationConflictError,
    PlatformUserInvitationValidationError,
    PlatformUserOrganizationBoundaryError,
    PlatformUserOrganizationNotActiveError,
    PlatformUserService,
)


ORG_A = "org-a"
ORG_B = "org-b"
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


def _service():
    db = MagicMock()
    service = PlatformUserService(db)

    service.organization_repository = MagicMock()
    service.organization_repository.get_by_id_for_update.return_value = (
        SimpleNamespace(
            id=ORG_A,
            status=OrganizationStatus.ACTIVE.value,
        )
    )

    service.platform_user_repository = MagicMock()
    service.platform_user_repository.get_by_external_identity.return_value = None

    def create(platform_user):
        platform_user.id = "invited-user-1"
        return platform_user

    service.platform_user_repository.create.side_effect = create
    service.audit_service = MagicMock()
    service.audit_service.record_pending.return_value = SimpleNamespace(
        id="audit-1"
    )

    return service, db


def _invite(service, **overrides):
    values = {
        "organization_id": ORG_A,
        "display_name": "  Jane Smith  ",
        "email": "  JANE@EXAMPLE.COM  ",
        "identity_provider": "  microsoft-entra  ",
        "external_tenant_id": "  tenant-a  ",
        "external_subject_id": "  subject-jane  ",
        "identity_issuer": "  https://issuer.example/tenant-a  ",
        "trusted_caller": _caller(),
    }
    values.update(overrides)
    return service.invite(**values)


def test_invite_creates_invited_non_bootstrap_user():
    service, db = _service()

    result = _invite(service)

    assert result.status == PlatformUserStatus.INVITED.value
    assert result.created_via_bootstrap is False
    assert result.organizational_identity_id is None
    assert result.display_name == "Jane Smith"
    assert result.email == "jane@example.com"
    assert result.identity_provider == "microsoft-entra"
    assert result.external_tenant_id == "tenant-a"
    assert result.external_subject_id == "subject-jane"
    assert result.activated_at is None
    assert result.last_authenticated_at is None
    assert result.created_by == "platform-user:admin-a"
    assert result.updated_by == "platform-user:admin-a"
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_invite_audits_without_granting_authority_or_binding_identity():
    service, _db = _service()

    _invite(service)

    kwargs = service.audit_service.record_pending.call_args.kwargs
    assert kwargs["event_type"] == "PlatformUserInvited"
    assert kwargs["actor"] == "platform-user:admin-a"
    assert kwargs["metadata"]["authorization_granted"] is False
    assert kwargs["metadata"]["seat_allocated"] is False
    assert kwargs["metadata"]["authentication_completed"] is False
    assert kwargs["metadata"]["organizational_identity_bound"] is False
    assert kwargs["metadata"]["actor_trust"] == "AuthenticatedPlatformCaller"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("display_name", " "),
        ("email", ""),
        ("identity_provider", " "),
        ("external_tenant_id", ""),
        ("external_subject_id", " "),
    ],
)
def test_invite_requires_identity_evidence(field_name, value):
    service, db = _service()

    with pytest.raises(PlatformUserInvitationValidationError):
        _invite(service, **{field_name: value})

    service.platform_user_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_invite_rejects_cross_organization_trusted_caller():
    service, db = _service()

    with pytest.raises(PlatformUserOrganizationBoundaryError):
        _invite(
            service,
            trusted_caller=_caller(organization_id=ORG_B),
        )

    service.organization_repository.get_by_id_for_update.assert_not_called()
    service.platform_user_repository.create.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_invite_requires_active_organization():
    service, db = _service()
    service.organization_repository.get_by_id_for_update.return_value = (
        SimpleNamespace(
            id=ORG_A,
            status="Suspended",
        )
    )

    with pytest.raises(PlatformUserOrganizationNotActiveError):
        _invite(service)

    service.platform_user_repository.create.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_invite_rejects_existing_external_identity():
    service, db = _service()
    service.platform_user_repository.get_by_external_identity.return_value = (
        SimpleNamespace(id="existing-user")
    )

    with pytest.raises(PlatformUserExternalIdentityConflictError):
        _invite(service)

    service.platform_user_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_invite_integrity_conflict_fails_closed_and_rolls_back():
    service, db = _service()
    service.platform_user_repository.create.side_effect = IntegrityError(
        "insert",
        {},
        Exception("conflict"),
    )

    with pytest.raises(PlatformUserInvitationConflictError):
        _invite(service)

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_invite_audit_failure_rolls_back():
    service, db = _service()
    service.audit_service.record_pending.side_effect = RuntimeError(
        "audit failure"
    )

    with pytest.raises(RuntimeError, match="audit failure"):
        _invite(service)

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_invite_does_not_query_bootstrap_license_or_bootstrap_state():
    service, _db = _service()
    service.license_repository = MagicMock()

    _invite(service)

    service.license_repository.get_bootstrap_eligible_license.assert_not_called()
    service.platform_user_repository.bootstrap_exists.assert_not_called()


def test_invite_does_not_assign_roles_or_permissions():
    service, _db = _service()

    result = _invite(service)

    assert not hasattr(result, "platform_role_id")
    assert not hasattr(result, "permission_key")
