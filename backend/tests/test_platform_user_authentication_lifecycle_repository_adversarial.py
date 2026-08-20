import inspect
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.repositories.platform_user_repository import (
    PlatformUserRepository,
)


def _method_source(name: str) -> str:
    return inspect.getsource(
        getattr(PlatformUserRepository, name)
    )


def test_gate_locked_lookup_uses_complete_external_identity_tuple():
    source = _method_source(
        "get_by_external_identity_for_update"
    )

    required = (
        "organization_id",
        "identity_provider",
        "external_tenant_id",
        "external_subject_id",
        "with_for_update",
    )

    for token in required:
        assert token in source


def test_gate_locked_lookup_does_not_use_email_or_display_name():
    source = _method_source(
        "get_by_external_identity_for_update"
    )

    assert "email" not in source
    assert "display_name" not in source


def test_gate_locked_lookup_does_not_authenticate_or_authorize():
    source = _method_source(
        "get_by_external_identity_for_update"
    )

    forbidden = (
        "jwt",
        "bearer",
        "token",
        "TrustedPlatformCaller",
        "PlatformRuntimeAuthorizationService",
        "grant_permission",
        "assign_role",
        "LicenseRepository",
        "SeatRepository",
    )

    lowered = source.lower()

    for token in forbidden:
        assert token.lower() not in lowered


def test_gate_first_authentication_mutates_only_expected_fields():
    db = MagicMock()

    platform_user = SimpleNamespace(
        status="Invited",
        activated_at=None,
        last_authenticated_at=None,
        updated_by="old",
        email="user@example.com",
        identity_provider="microsoft-entra",
        external_tenant_id="tenant",
        external_subject_id="subject",
        identity_issuer="issuer",
        is_active=True,
        created_via_bootstrap=False,
        organization_id="org-a",
    )

    snapshot = dict(platform_user.__dict__)

    authenticated_at = datetime(
        2026,
        8,
        20,
        18,
        0,
        tzinfo=UTC,
    )

    PlatformUserRepository(db).record_first_authentication(
        platform_user=platform_user,
        activated_at=authenticated_at,
        updated_by="authenticated-principal",
    )

    expected_changed = {
        "status",
        "activated_at",
        "last_authenticated_at",
        "updated_by",
    }

    for field, original_value in snapshot.items():
        if field in expected_changed:
            continue
        assert getattr(platform_user, field) == original_value


def test_gate_first_authentication_does_not_change_record_lifecycle():
    db = MagicMock()

    platform_user = SimpleNamespace(
        status="Invited",
        activated_at=None,
        last_authenticated_at=None,
        updated_by=None,
        is_active=True,
    )

    PlatformUserRepository(db).record_first_authentication(
        platform_user=platform_user,
        activated_at=datetime.now(UTC),
        updated_by="authenticated-principal",
    )

    assert platform_user.is_active is True


def test_gate_first_authentication_does_not_commit_rollback_or_audit():
    source = _method_source(
        "record_first_authentication"
    )

    forbidden = (
        ".commit(",
        ".rollback(",
        "record_pending",
        "AuditService",
    )

    for token in forbidden:
        assert token not in source


def test_gate_first_authentication_does_not_evaluate_invitation_policy():
    source = _method_source(
        "record_first_authentication"
    )

    forbidden = (
        "PlatformUserStatus.INVITED",
        "identity_issuer",
        "external_tenant_id",
        "external_subject_id",
        "identity_provider",
        "TrustedExternalPrincipal",
    )

    for token in forbidden:
        assert token not in source


def test_gate_first_authentication_has_no_provider_specific_coupling():
    source = _method_source(
        "record_first_authentication"
    )

    lowered = source.lower()

    forbidden = (
        "microsoft",
        "entra",
        "okta",
        "google",
        "securew2",
    )

    for token in forbidden:
        assert token not in lowered


def test_gate_locked_lookup_has_no_provider_specific_coupling():
    source = _method_source(
        "get_by_external_identity_for_update"
    )

    lowered = source.lower()

    forbidden = (
        "microsoft",
        "entra",
        "okta",
        "google",
        "securew2",
    )

    for token in forbidden:
        assert token not in lowered


def test_gate_first_authentication_refreshes_but_does_not_own_transaction():
    db = MagicMock()

    platform_user = SimpleNamespace(
        status="Invited",
        activated_at=None,
        last_authenticated_at=None,
        updated_by=None,
    )

    repository = PlatformUserRepository(db)

    repository.record_first_authentication(
        platform_user=platform_user,
        activated_at=datetime.now(UTC),
        updated_by="authenticated-principal",
    )

    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(platform_user)
    db.commit.assert_not_called()
    db.rollback.assert_not_called()
