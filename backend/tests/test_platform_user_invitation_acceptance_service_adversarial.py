import inspect
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_user_invitation_acceptance_service import (
    PlatformUserInvitationAcceptanceService,
    PlatformUserInvitationIssuerMismatchError,
    PlatformUserInvitationNotAcceptableError,
    PlatformUserInvitationNotFoundError,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


NOW = datetime(
    2026,
    8,
    20,
    22,
    0,
    tzinfo=UTC,
)


def _principal(
    *,
    provider="microsoft-entra",
    tenant="tenant-a",
    subject="subject-a",
    issuer="issuer-a",
):
    return TrustedExternalPrincipal(
        identity_provider=provider,
        external_tenant_id=tenant,
        external_subject_id=subject,
        issuer=issuer,
        authenticated_at=NOW,
    )


def _user(
    *,
    status=PlatformUserStatus.INVITED.value,
    issuer="issuer-a",
    is_active=True,
):
    return SimpleNamespace(
        id="user-a",
        organization_id="org-a",
        display_name="User A",
        status=status,
        identity_issuer=issuer,
        is_active=is_active,
    )


def _harness(target):
    db = MagicMock()

    repository = MagicMock()
    repository.get_by_external_identity_for_update.return_value = (
        target
    )
    repository.record_first_authentication.side_effect = (
        lambda **kwargs: kwargs["platform_user"]
    )

    audit = MagicMock()
    audit.record_pending.return_value = (
        SimpleNamespace(id="audit-a")
    )

    service = PlatformUserInvitationAcceptanceService(
        db,
        platform_user_repository=repository,
        audit_service=audit,
    )

    return service, db, repository, audit


def test_gate_service_accepts_only_trusted_external_principal():
    service, db, repository, audit = _harness(
        _user()
    )

    with pytest.raises(TypeError):
        service.accept(
            organization_id="org-a",
            principal=SimpleNamespace(
                identity_provider="microsoft-entra",
                external_tenant_id="tenant-a",
                external_subject_id="subject-a",
                issuer="issuer-a",
                authenticated_at=NOW,
            ),
        )

    repository.get_by_external_identity_for_update.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_gate_service_never_uses_email_for_invitation_matching():
    source = inspect.getsource(
        PlatformUserInvitationAcceptanceService.accept
    )

    assert "email" not in source
    assert "display_name" not in source.split(
        "get_by_external_identity_for_update",
        1,
    )[0]


def test_gate_service_requires_locked_external_identity_lookup():
    source = inspect.getsource(
        PlatformUserInvitationAcceptanceService.accept
    )

    assert "get_by_external_identity_for_update" in source
    assert "get_by_external_identity(" not in source


def test_gate_provider_tenant_subject_come_only_from_principal():
    target = _user()
    service, _, repository, _ = _harness(
        target
    )

    principal = _principal(
        provider="okta",
        tenant="tenant-z",
        subject="subject-z",
    )

    service.accept(
        organization_id="org-a",
        principal=principal,
    )

    repository.get_by_external_identity_for_update.assert_called_once_with(
        organization_id="org-a",
        identity_provider="okta",
        external_tenant_id="tenant-z",
        external_subject_id="subject-z",
    )


def test_gate_wrong_issuer_cannot_mutate_or_audit():
    service, db, repository, audit = _harness(
        _user(issuer="expected")
    )

    with pytest.raises(
        PlatformUserInvitationIssuerMismatchError
    ):
        service.accept(
            organization_id="org-a",
            principal=_principal(
                issuer="wrong"
            ),
        )

    repository.record_first_authentication.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_gate_non_invited_states_cannot_cross_trust_boundary():
    for status in (
        PlatformUserStatus.ACTIVE.value,
        PlatformUserStatus.SUSPENDED.value,
        PlatformUserStatus.DISABLED.value,
    ):
        service, db, repository, audit = _harness(
            _user(status=status)
        )

        with pytest.raises(
            PlatformUserInvitationNotAcceptableError
        ):
            service.accept(
                organization_id="org-a",
                principal=_principal(),
            )

        repository.record_first_authentication.assert_not_called()
        audit.record_pending.assert_not_called()
        db.commit.assert_not_called()
        db.rollback.assert_called_once_with()


def test_gate_missing_invitation_cannot_create_user_or_authority():
    service, db, repository, audit = _harness(
        None
    )

    with pytest.raises(
        PlatformUserInvitationNotFoundError
    ):
        service.accept(
            organization_id="org-a",
            principal=_principal(),
        )

    repository.record_first_authentication.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_gate_service_does_not_grant_roles_permissions_seats_or_license():
    source = inspect.getsource(
        PlatformUserInvitationAcceptanceService
    )

    forbidden = (
        "PlatformRuntimeAuthorizationService",
        "PlatformAuthorizationService",
        "assign_role",
        "grant_permission",
        "LicenseRepository",
        "SeatRepository",
        "seat_allocated = True",
        "authorization_granted = True",
    )

    for token in forbidden:
        assert token not in source


def test_gate_service_does_not_validate_raw_credentials():
    source = inspect.getsource(
        PlatformUserInvitationAcceptanceService
    ).lower()

    forbidden = (
        "jwt.decode",
        "bearer",
        "access_token",
        "refresh_token",
        "password",
        "jwk",
    )

    for token in forbidden:
        assert token not in source


def test_gate_audit_failure_prevents_commit():
    service, db, _, audit = _harness(
        _user()
    )

    audit.record_pending.side_effect = RuntimeError(
        "audit unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="audit unavailable",
    ):
        service.accept(
            organization_id="org-a",
            principal=_principal(),
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_gate_commit_failure_rolls_back_transaction():
    service, db, _, _ = _harness(
        _user()
    )

    db.commit.side_effect = RuntimeError(
        "commit unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="commit unavailable",
    ):
        service.accept(
            organization_id="org-a",
            principal=_principal(),
        )

    db.rollback.assert_called_once_with()


def test_gate_audit_explicitly_denies_authority_and_seat_side_effects():
    service, _, _, audit = _harness(
        _user()
    )

    service.accept(
        organization_id="org-a",
        principal=_principal(),
    )

    metadata = (
        audit.record_pending.call_args.kwargs[
            "metadata"
        ]
    )

    assert (
        metadata[
            "authorization_granted_by_transition"
        ]
        is False
    )
    assert (
        metadata[
            "seat_allocated_by_transition"
        ]
        is False
    )
    assert metadata["authentication_completed"] is True


def test_gate_service_is_provider_neutral():
    source = inspect.getsource(
        PlatformUserInvitationAcceptanceService
    ).lower()

    forbidden = (
        "microsoft-entra",
        "okta",
        "google",
        "securew2",
    )

    for token in forbidden:
        assert token not in source
