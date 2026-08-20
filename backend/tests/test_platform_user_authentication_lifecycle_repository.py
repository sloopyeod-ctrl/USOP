from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.repositories.platform_user_repository import (
    PlatformUserRepository,
)


def _query_chain(result):
    query = MagicMock()
    query.filter.return_value = query
    query.with_for_update.return_value = query
    query.one_or_none.return_value = result
    return query


def test_external_identity_for_update_uses_row_lock():
    db = MagicMock()
    platform_user = SimpleNamespace(id="user-1")
    query = _query_chain(platform_user)
    db.query.return_value = query

    repository = PlatformUserRepository(db)

    result = repository.get_by_external_identity_for_update(
        organization_id="org-a",
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-a",
    )

    assert result is platform_user
    query.with_for_update.assert_called_once_with()


def test_external_identity_for_update_returns_none_when_missing():
    db = MagicMock()
    query = _query_chain(None)
    db.query.return_value = query

    repository = PlatformUserRepository(db)

    result = repository.get_by_external_identity_for_update(
        organization_id="org-a",
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="missing",
    )

    assert result is None


def test_record_first_authentication_persists_lifecycle_facts():
    db = MagicMock()

    platform_user = SimpleNamespace(
        status="Invited",
        activated_at=None,
        last_authenticated_at=None,
        updated_by="old-actor",
    )

    authenticated_at = datetime(
        2026,
        8,
        20,
        17,
        30,
        tzinfo=UTC,
    )

    repository = PlatformUserRepository(db)

    result = repository.record_first_authentication(
        platform_user=platform_user,
        activated_at=authenticated_at,
        updated_by="authenticated-principal",
    )

    assert result is platform_user
    assert platform_user.status == "Active"
    assert platform_user.activated_at == authenticated_at
    assert platform_user.last_authenticated_at == authenticated_at
    assert platform_user.updated_by == "authenticated-principal"

    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(platform_user)


def test_record_first_authentication_does_not_commit_or_rollback():
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

    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_repository_authentication_lifecycle_methods_do_not_accept_tokens():
    import inspect

    source = inspect.getsource(
        PlatformUserRepository.record_first_authentication
    )

    lowered = source.lower()

    assert "token" not in lowered
    assert "bearer" not in lowered
    assert "jwt" not in lowered


def test_repository_authentication_lifecycle_methods_do_not_authorize():
    import inspect

    source = inspect.getsource(
        PlatformUserRepository.record_first_authentication
    )

    forbidden = (
        "TrustedPlatformCaller",
        "PlatformRuntimeAuthorizationService",
        "grant_permission",
        "assign_role",
        "LicenseRepository",
        "SeatRepository",
    )

    for token in forbidden:
        assert token not in source
