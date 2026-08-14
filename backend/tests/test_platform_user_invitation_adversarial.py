import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.organization_status import OrganizationStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_user_service import (
    AUTHENTICATED_PLATFORM_USER_ACTOR_PREFIX,
    PlatformUserExternalIdentityConflictError,
    PlatformUserInvitationConflictError,
    PlatformUserInvitationValidationError,
    PlatformUserOrganizationBoundaryError,
    PlatformUserOrganizationNotActiveError,
    PlatformUserOrganizationNotFoundError,
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
        "display_name": "Jane Smith",
        "email": "jane@example.com",
        "identity_provider": "microsoft-entra",
        "external_tenant_id": "tenant-a",
        "external_subject_id": "subject-jane",
        "identity_issuer": "https://issuer.example/tenant-a",
        "trusted_caller": _caller(),
    }
    values.update(overrides)
    return service.invite(**values)


def test_gate_invite_signature_has_no_authority_or_state_injection_operands():
    signature = inspect.signature(PlatformUserService.invite)

    forbidden = {
        "actor",
        "created_by",
        "updated_by",
        "status",
        "created_via_bootstrap",
        "organizational_identity_id",
        "platform_role_id",
        "permission_key",
        "seat_allocated",
        "authorization_granted",
        "activated_at",
        "last_authenticated_at",
        "evaluated_at",
        "now",
        "timestamp",
    }

    assert forbidden.isdisjoint(signature.parameters)


def test_gate_invite_requires_trusted_caller():
    service, db = _service()

    with pytest.raises(PlatformUserOrganizationBoundaryError):
        _invite(service, trusted_caller=None)

    service.organization_repository.get_by_id_for_update.assert_not_called()
    service.platform_user_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_cross_organization_actor_fails_before_lock_or_create():
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


def test_gate_actor_attribution_is_server_derived():
    service, _db = _service()

    _invite(
        service,
        trusted_caller=_caller(platform_user_id="immutable-admin-id"),
    )

    audit_kwargs = service.audit_service.record_pending.call_args.kwargs
    assert audit_kwargs["actor"] == (
        f"{AUTHENTICATED_PLATFORM_USER_ACTOR_PREFIX}"
        "immutable-admin-id"
    )
    assert audit_kwargs["metadata"]["actor_platform_user_id"] == (
        "immutable-admin-id"
    )
    assert audit_kwargs["metadata"]["actor_trust"] == (
        "AuthenticatedPlatformCaller"
    )


def test_gate_unknown_organization_fails_closed():
    service, db = _service()
    service.organization_repository.get_by_id_for_update.return_value = None

    with pytest.raises(PlatformUserOrganizationNotFoundError):
        _invite(service)

    service.platform_user_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_inactive_organization_cannot_invite():
    service, db = _service()
    service.organization_repository.get_by_id_for_update.return_value = (
        SimpleNamespace(id=ORG_A, status="Suspended")
    )

    with pytest.raises(PlatformUserOrganizationNotActiveError):
        _invite(service)

    service.platform_user_repository.create.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_external_identity_uniqueness_is_org_scoped_and_complete():
    service, _db = _service()

    _invite(service)

    service.platform_user_repository.get_by_external_identity.assert_called_once_with(
        organization_id=ORG_A,
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-jane",
    )


def test_gate_duplicate_external_identity_fails_before_create():
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


def test_gate_invited_user_cannot_be_smuggled_as_active_or_bootstrap():
    service, _db = _service()

    result = _invite(service)

    assert result.status == PlatformUserStatus.INVITED.value
    assert result.created_via_bootstrap is False
    assert result.activated_at is None
    assert result.last_authenticated_at is None


def test_gate_invitation_never_auto_binds_organizational_identity():
    service, _db = _service()

    result = _invite(service)

    assert result.organizational_identity_id is None
    audit_kwargs = service.audit_service.record_pending.call_args.kwargs
    assert audit_kwargs["metadata"]["organizational_identity_bound"] is False


def test_gate_invitation_never_queries_binding_service_or_correlation_service():
    source = inspect.getsource(PlatformUserService._invite_pending)

    forbidden = [
        "PlatformUserIdentityBindingService",
        "PlatformUserIdentityCorrelationService",
        ".bind(",
        ".evaluate(",
    ]

    for fragment in forbidden:
        assert fragment not in source


def test_gate_invitation_never_queries_bootstrap_license_or_bootstrap_exists():
    service, _db = _service()
    service.license_repository = MagicMock()

    _invite(service)

    service.license_repository.get_bootstrap_eligible_license.assert_not_called()
    service.platform_user_repository.bootstrap_exists.assert_not_called()


def test_gate_invitation_audit_records_no_authority_side_effects():
    service, _db = _service()

    _invite(service)

    metadata = service.audit_service.record_pending.call_args.kwargs["metadata"]
    assert metadata["authorization_granted"] is False
    assert metadata["seat_allocated"] is False
    assert metadata["authentication_completed"] is False
    assert metadata["created_via_bootstrap"] is False


def test_gate_integrity_error_never_commits_partial_invitation():
    service, db = _service()
    service.platform_user_repository.create.side_effect = IntegrityError(
        "insert",
        {},
        Exception("unique violation"),
    )

    with pytest.raises(PlatformUserInvitationConflictError):
        _invite(service)

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    service.audit_service.record_pending.assert_not_called()


def test_gate_audit_failure_rolls_back_and_never_commits():
    service, db = _service()
    service.audit_service.record_pending.side_effect = RuntimeError(
        "audit unavailable"
    )

    with pytest.raises(RuntimeError, match="audit unavailable"):
        _invite(service)

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_commit_failure_rolls_back():
    service, db = _service()
    db.commit.side_effect = RuntimeError("commit failure")

    with pytest.raises(RuntimeError, match="commit failure"):
        _invite(service)

    db.rollback.assert_called_once()


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("organization_id", ""),
        ("display_name", ""),
        ("email", " "),
        ("identity_provider", ""),
        ("external_tenant_id", " "),
        ("external_subject_id", ""),
    ],
)
def test_gate_required_values_fail_closed(field_name, value):
    service, db = _service()

    with pytest.raises(PlatformUserInvitationValidationError):
        _invite(service, **{field_name: value})

    service.platform_user_repository.create.assert_not_called()
    service.audit_service.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_gate_email_is_normalized_but_not_used_as_authorization_identity():
    service, _db = _service()

    result = _invite(
        service,
        email="  ADMIN@EXAMPLE.COM  ",
    )

    assert result.email == "admin@example.com"

    audit_kwargs = service.audit_service.record_pending.call_args.kwargs
    assert audit_kwargs["actor"] == "platform-user:admin-a"
    assert audit_kwargs["actor"] != result.email


def test_gate_identity_provider_tenant_subject_are_normalized_before_lookup():
    service, _db = _service()

    _invite(
        service,
        identity_provider="  microsoft-entra  ",
        external_tenant_id="  tenant-a  ",
        external_subject_id="  subject-jane  ",
    )

    service.platform_user_repository.get_by_external_identity.assert_called_once_with(
        organization_id=ORG_A,
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-jane",
    )


def test_gate_invitation_operation_does_not_call_runtime_authorization_itself():
    service, _db = _service()
    service.runtime_authorization_service = MagicMock()

    _invite(service)

    service.runtime_authorization_service.has_permission.assert_not_called()


def test_gate_schema_forbids_extra_authority_fields():
    from pydantic import ValidationError

    from app.schemas.platform_user import PlatformUserInvite

    with pytest.raises(ValidationError):
        PlatformUserInvite(
            display_name="Jane Smith",
            email="jane@example.com",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-jane",
            status="Active",
        )
