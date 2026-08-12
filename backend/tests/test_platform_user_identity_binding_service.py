from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.platform_user_identity_binding_service import (
    PlatformUserIdentityBindingActorRequiredError,
    PlatformUserIdentityBindingOrganizationalIdentityNotFoundError,
    PlatformUserIdentityBindingPlatformUserNotFoundError,
    PlatformUserIdentityBindingService,
)


ORGANIZATION_ID = "organization-027"
PLATFORM_USER_ID = "platform-user-001"
ORGANIZATIONAL_IDENTITY_ID = "organizational-identity-001"


def build_service(*, platform_user=None, organizational_identity=None):
    db = MagicMock()
    organization_repository = MagicMock()
    platform_user_repository = MagicMock()
    organizational_identity_repository = MagicMock()
    audit_service = MagicMock()

    organization_repository.get_by_id.return_value = SimpleNamespace(
        id=ORGANIZATION_ID
    )
    platform_user_repository.get_by_id.return_value = platform_user
    organizational_identity_repository.get_by_id_for_organization.return_value = (
        organizational_identity
    )

    platform_user_repository.set_organizational_identity_binding.side_effect = (
        lambda *, platform_user, organizational_identity_id: (
            setattr(
                platform_user,
                "organizational_identity_id",
                organizational_identity_id,
            )
            or platform_user
        )
    )
    audit_service.record_pending.return_value = SimpleNamespace(id="audit-001")

    service = PlatformUserIdentityBindingService(
        db,
        organization_repository=organization_repository,
        platform_user_repository=platform_user_repository,
        organizational_identity_repository=(
            organizational_identity_repository
        ),
        audit_service=audit_service,
    )

    return (
        service,
        db,
        platform_user_repository,
        organizational_identity_repository,
        audit_service,
    )


def make_platform_user(
    *,
    organization_id=ORGANIZATION_ID,
    organizational_identity_id=None,
):
    return SimpleNamespace(
        id=PLATFORM_USER_ID,
        organization_id=organization_id,
        organizational_identity_id=organizational_identity_id,
        display_name="Geoff Dewitt",
        updated_by=None,
    )


def make_organizational_identity():
    return SimpleNamespace(
        id=ORGANIZATIONAL_IDENTITY_ID,
        organization_id=ORGANIZATION_ID,
        identity_id="identity-001",
    )


def test_bind_requires_explicit_actor():
    service, db, platform_repo, oi_repo, audit = build_service(
        platform_user=make_platform_user(),
        organizational_identity=make_organizational_identity(),
    )

    with pytest.raises(PlatformUserIdentityBindingActorRequiredError):
        service.bind(
            organization_id=ORGANIZATION_ID,
            platform_user_id=PLATFORM_USER_ID,
            organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID,
            actor="   ",
        )

    platform_repo.set_organizational_identity_binding.assert_not_called()
    oi_repo.get_by_id_for_organization.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()


def test_bind_rejects_platform_user_from_another_organization():
    service, db, platform_repo, oi_repo, audit = build_service(
        platform_user=make_platform_user(
            organization_id="organization-075"
        ),
        organizational_identity=make_organizational_identity(),
    )

    with pytest.raises(
        PlatformUserIdentityBindingPlatformUserNotFoundError
    ):
        service.bind(
            organization_id=ORGANIZATION_ID,
            platform_user_id=PLATFORM_USER_ID,
            organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID,
            actor="platform-admin",
        )

    oi_repo.get_by_id_for_organization.assert_not_called()
    platform_repo.set_organizational_identity_binding.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()


def test_bind_rejects_unknown_or_cross_organization_identity():
    service, db, platform_repo, oi_repo, audit = build_service(
        platform_user=make_platform_user(),
        organizational_identity=None,
    )

    with pytest.raises(
        PlatformUserIdentityBindingOrganizationalIdentityNotFoundError
    ):
        service.bind(
            organization_id=ORGANIZATION_ID,
            platform_user_id=PLATFORM_USER_ID,
            organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID,
            actor="platform-admin",
        )

    oi_repo.get_by_id_for_organization.assert_called_once_with(
        organization_id=ORGANIZATION_ID,
        organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID,
    )
    platform_repo.set_organizational_identity_binding.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()


def test_bind_is_idempotent_for_same_relationship():
    user = make_platform_user(
        organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID
    )
    service, db, platform_repo, _oi_repo, audit = build_service(
        platform_user=user,
        organizational_identity=make_organizational_identity(),
    )

    result = service.bind(
        organization_id=ORGANIZATION_ID,
        platform_user_id=PLATFORM_USER_ID,
        organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID,
        actor="platform-admin",
    )

    assert result is user
    platform_repo.set_organizational_identity_binding.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()


def test_bind_commits_and_audits_authoritative_relationship():
    user = make_platform_user()
    service, db, _platform_repo, _oi_repo, audit = build_service(
        platform_user=user,
        organizational_identity=make_organizational_identity(),
    )

    result = service.bind(
        organization_id=ORGANIZATION_ID,
        platform_user_id=PLATFORM_USER_ID,
        organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID,
        actor="platform-admin",
    )

    assert result.organizational_identity_id == ORGANIZATIONAL_IDENTITY_ID
    assert result.updated_by == "platform-admin"

    audit_kwargs = audit.record_pending.call_args.kwargs
    assert audit_kwargs["event_type"] == "PlatformUserIdentityBound"
    assert audit_kwargs["metadata"]["organization_id"] == ORGANIZATION_ID
    assert audit_kwargs["metadata"]["identity_id"] == "identity-001"
    assert audit_kwargs["metadata"]["correlation_method"] == "ExplicitBinding"

    db.commit.assert_called_once()


def test_unbind_is_idempotent_when_no_relationship_exists():
    user = make_platform_user()
    service, db, platform_repo, _oi_repo, audit = build_service(
        platform_user=user,
    )

    result = service.unbind(
        organization_id=ORGANIZATION_ID,
        platform_user_id=PLATFORM_USER_ID,
        actor="platform-admin",
    )

    assert result is user
    platform_repo.set_organizational_identity_binding.assert_not_called()
    audit.record_pending.assert_not_called()
    db.commit.assert_not_called()


def test_unbind_commits_and_audits_previous_relationship():
    user = make_platform_user(
        organizational_identity_id=ORGANIZATIONAL_IDENTITY_ID
    )
    service, db, _platform_repo, _oi_repo, audit = build_service(
        platform_user=user,
    )

    result = service.unbind(
        organization_id=ORGANIZATION_ID,
        platform_user_id=PLATFORM_USER_ID,
        actor="platform-admin",
    )

    assert result.organizational_identity_id is None

    audit_kwargs = audit.record_pending.call_args.kwargs
    assert audit_kwargs["event_type"] == "PlatformUserIdentityUnbound"
    assert (
        audit_kwargs["metadata"]["previous_organizational_identity_id"]
        == ORGANIZATIONAL_IDENTITY_ID
    )

    db.commit.assert_called_once()
