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
    21,
    0,
    tzinfo=UTC,
)


def _principal(
    issuer="issuer-a",
):
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-a",
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
    (
        repository
        .get_by_external_identity_for_update
        .return_value
    ) = target
    (
        repository
        .record_first_authentication
        .side_effect
    ) = lambda **kwargs: kwargs["platform_user"]

    audit_service = MagicMock()
    audit_service.record_pending.return_value = (
        SimpleNamespace(id="audit-a")
    )

    service = PlatformUserInvitationAcceptanceService(
        db,
        platform_user_repository=repository,
        audit_service=audit_service,
    )

    return (
        service,
        db,
        repository,
        audit_service,
    )


def test_accept_uses_exact_authenticated_identity_coordinates():
    service, _, repository, _ = _harness(
        _user()
    )

    service.accept(
        organization_id="org-a",
        principal=_principal(),
    )

    (
        repository
        .get_by_external_identity_for_update
        .assert_called_once_with(
            organization_id="org-a",
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-a",
        )
    )


def test_accept_records_first_authentication_and_audit_atomically():
    target = _user()
    service, db, repository, audit = _harness(
        target
    )

    result = service.accept(
        organization_id="org-a",
        principal=_principal(),
    )

    assert result is target

    call = (
        repository
        .record_first_authentication
        .call_args
        .kwargs
    )

    assert call["platform_user"] is target
    assert call["activated_at"] == NOW
    assert call["updated_by"].startswith(
        "authenticated-external-principal:"
    )

    assert (
        audit.record_pending.call_args.kwargs[
            "event_type"
        ]
        == "PlatformUserInvitationAccepted"
    )

    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()


def test_accept_rejects_missing_invitation():
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

    (
        repository
        .record_first_authentication
        .assert_not_called()
    )
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


@pytest.mark.parametrize(
    "status",
    [
        PlatformUserStatus.ACTIVE.value,
        PlatformUserStatus.SUSPENDED.value,
        PlatformUserStatus.DISABLED.value,
    ],
)
def test_accept_requires_invited_lifecycle(
    status,
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

    (
        repository
        .record_first_authentication
        .assert_not_called()
    )
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_accept_rejects_inactive_record():
    service, db, repository, audit = _harness(
        _user(is_active=False)
    )

    with pytest.raises(
        PlatformUserInvitationNotAcceptableError
    ):
        service.accept(
            organization_id="org-a",
            principal=_principal(),
        )

    (
        repository
        .record_first_authentication
        .assert_not_called()
    )
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_accept_rejects_bound_issuer_mismatch():
    service, db, repository, audit = _harness(
        _user(issuer="expected")
    )

    with pytest.raises(
        PlatformUserInvitationIssuerMismatchError
    ):
        service.accept(
            organization_id="org-a",
            principal=_principal(
                issuer="presented"
            ),
        )

    (
        repository
        .record_first_authentication
        .assert_not_called()
    )
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_accept_allows_unbound_issuer():
    service, db, _, audit = _harness(
        _user(issuer=None)
    )

    result = service.accept(
        organization_id="org-a",
        principal=_principal(None),
    )

    assert result is not None
    db.commit.assert_called_once_with()
    audit.record_pending.assert_called_once()


def test_accept_audit_failure_rolls_back():
    service, db, _, audit = _harness(
        _user()
    )

    audit.record_pending.side_effect = (
        RuntimeError("audit unavailable")
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


def test_accept_commit_failure_rolls_back():
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


def test_accept_requires_trusted_external_principal():
    service, db, repository, audit = _harness(
        _user()
    )

    with pytest.raises(
        TypeError,
        match="TrustedExternalPrincipal",
    ):
        service.accept(
            organization_id="org-a",
            principal=object(),
        )

    (
        repository
        .get_by_external_identity_for_update
        .assert_not_called()
    )
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()
