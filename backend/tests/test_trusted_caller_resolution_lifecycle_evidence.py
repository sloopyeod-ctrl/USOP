from types import SimpleNamespace

import pytest

from app.domain.platform_user_status import PlatformUserStatus
from app.services.trusted_caller_identity_service import (
    TrustedCallerIdentityService,
)
from app.services.trusted_caller_resolution_result import (
    TrustedCallerResolutionDisposition,
    TrustedCallerResolutionResult,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


def _principal():
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-a",
        issuer="issuer-a",
    )


def _service(platform_user):
    class Repository:
        def get_by_external_identity(self, **kwargs):
            return platform_user

    return TrustedCallerIdentityService(
        object(),
        platform_user_repository=Repository(),
    )


def _user(
    *,
    status,
    is_active=True,
    issuer="issuer-a",
):
    return SimpleNamespace(
        id="user-a",
        status=status,
        is_active=is_active,
        identity_issuer=issuer,
    )


def test_resolution_result_defaults_status_to_none():
    result = TrustedCallerResolutionResult(
        disposition=TrustedCallerResolutionDisposition.NO_MATCH,
        organization_id="org-a",
        reason="test",
    )
    assert result.platform_user_status is None


def test_no_match_has_no_platform_user_status():
    result = _service(None).resolve(
        organization_id="org-a",
        principal=_principal(),
    )
    assert result.disposition == TrustedCallerResolutionDisposition.NO_MATCH
    assert result.platform_user_status is None


def test_inactive_record_carries_structured_lifecycle_status():
    result = _service(
        _user(
            status=PlatformUserStatus.INVITED.value,
            is_active=False,
        )
    ).resolve(
        organization_id="org-a",
        principal=_principal(),
    )
    assert (
        result.disposition
        == TrustedCallerResolutionDisposition.PLATFORM_USER_INACTIVE
    )
    assert result.platform_user_status == PlatformUserStatus.INVITED.value


@pytest.mark.parametrize(
    "status",
    [
        PlatformUserStatus.INVITED.value,
        PlatformUserStatus.SUSPENDED.value,
        PlatformUserStatus.DISABLED.value,
    ],
)
def test_non_active_lifecycle_carries_structured_status(status):
    result = _service(
        _user(status=status)
    ).resolve(
        organization_id="org-a",
        principal=_principal(),
    )
    assert (
        result.disposition
        == TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE
    )
    assert result.platform_user_status == status


def test_issuer_mismatch_carries_active_status():
    result = _service(
        _user(
            status=PlatformUserStatus.ACTIVE.value,
            issuer="expected-issuer",
        )
    ).resolve(
        organization_id="org-a",
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-a",
            external_subject_id="subject-a",
            issuer="presented-issuer",
        ),
    )
    assert (
        result.disposition
        == TrustedCallerResolutionDisposition.ISSUER_MISMATCH
    )
    assert result.platform_user_status == PlatformUserStatus.ACTIVE.value


def test_resolved_caller_carries_active_status():
    result = _service(
        _user(status=PlatformUserStatus.ACTIVE.value)
    ).resolve(
        organization_id="org-a",
        principal=_principal(),
    )
    assert result.resolved is True
    assert result.platform_user_status == PlatformUserStatus.ACTIVE.value
