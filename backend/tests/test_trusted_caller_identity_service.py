from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.domain.platform_user_status import PlatformUserStatus
from app.services.trusted_caller_identity_service import (
    TrustedCallerIdentityService,
)
from app.services.trusted_caller_resolution_result import (
    TrustedCallerResolutionDisposition,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


ORG_42 = "org-42"


def principal(**overrides):
    values = dict(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-42",
        external_subject_id="subject-42",
        issuer="https://login.example/tenant-42/v2.0",
    )
    values.update(overrides)
    return TrustedExternalPrincipal(**values)


def platform_user(**overrides):
    values = dict(
        id="platform-user-42",
        organization_id=ORG_42,
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-42",
        external_subject_id="subject-42",
        identity_issuer="https://login.example/tenant-42/v2.0",
        status=PlatformUserStatus.ACTIVE.value,
        is_active=True,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def build(user_record):
    db = MagicMock()
    repo = MagicMock()
    repo.get_by_external_identity.return_value = user_record

    service = TrustedCallerIdentityService(
        db,
        platform_user_repository=repo,
    )

    return service, repo


def test_exact_external_identity_resolves_active_platform_user():
    service, repo = build(platform_user())

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(),
    )

    assert result.resolved is True
    assert result.caller.platform_user_id == "platform-user-42"
    assert result.caller.organization_id == ORG_42

    repo.get_by_external_identity.assert_called_once_with(
        organization_id=ORG_42,
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-42",
        external_subject_id="subject-42",
    )


def test_no_match_fails_closed():
    service, _repo = build(None)

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(),
    )

    assert result.resolved is False
    assert result.disposition == (
        TrustedCallerResolutionDisposition.NO_MATCH
    )


@pytest.mark.parametrize(
    "status",
    [
        PlatformUserStatus.INVITED.value,
        PlatformUserStatus.SUSPENDED.value,
        PlatformUserStatus.DISABLED.value,
    ],
)
def test_non_active_lifecycle_cannot_be_trusted_caller(status):
    service, _repo = build(
        platform_user(status=status)
    )

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(),
    )

    assert result.resolved is False
    assert result.disposition == (
        TrustedCallerResolutionDisposition
        .PLATFORM_USER_NOT_ACTIVE
    )


def test_inactive_platform_user_record_cannot_resolve():
    service, _repo = build(
        platform_user(is_active=False)
    )

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(),
    )

    assert result.resolved is False
    assert result.disposition == (
        TrustedCallerResolutionDisposition
        .PLATFORM_USER_INACTIVE
    )


def test_configured_issuer_must_match():
    service, _repo = build(platform_user())

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(
            issuer="https://different.example/",
        ),
    )

    assert result.resolved is False
    assert result.disposition == (
        TrustedCallerResolutionDisposition.ISSUER_MISMATCH
    )


def test_missing_presented_issuer_fails_if_platform_user_requires_one():
    service, _repo = build(platform_user())

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(issuer=None),
    )

    assert result.resolved is False
    assert result.disposition == (
        TrustedCallerResolutionDisposition.ISSUER_MISMATCH
    )


def test_unconfigured_platform_user_issuer_does_not_invent_policy():
    service, _repo = build(
        platform_user(identity_issuer=None)
    )

    result = service.resolve(
        organization_id=ORG_42,
        principal=principal(issuer=None),
    )

    assert result.resolved is True


def test_raw_dict_is_rejected_as_untrusted_input():
    service, repo = build(platform_user())

    with pytest.raises(TypeError):
        service.resolve(
            organization_id=ORG_42,
            principal={
                "identity_provider": "microsoft-entra",
                "external_tenant_id": "tenant-42",
                "external_subject_id": "subject-42",
            },
        )

    repo.get_by_external_identity.assert_not_called()
