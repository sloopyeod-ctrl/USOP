from unittest.mock import MagicMock

import pytest

from app.domain.platform_user_status import PlatformUserStatus
from app.services.platform_authentication_composition_service import (
    PlatformAuthenticationCompositionError,
    PlatformAuthenticationCompositionService,
)
from app.services.trusted_caller_resolution_result import (
    TrustedCallerResolutionDisposition,
    TrustedCallerResolutionResult,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)
from app.services.trusted_platform_caller import (
    TrustedPlatformCaller,
)


ORG = "org-a"


def _principal():
    return TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-a",
        external_subject_id="subject-a",
        issuer="issuer-a",
    )


def _caller(principal):
    return TrustedPlatformCaller(
        organization_id=ORG,
        platform_user_id="user-a",
        principal=principal,
    )


def _result(
    disposition,
    *,
    status=None,
    caller=None,
):
    return TrustedCallerResolutionResult(
        disposition=disposition,
        organization_id=ORG,
        reason="test",
        platform_user_id=(
            "user-a"
            if disposition
            != TrustedCallerResolutionDisposition.NO_MATCH
            else None
        ),
        platform_user_status=status,
        caller=caller,
    )


def test_already_resolved_caller_does_not_accept_invitation():
    principal = _principal()
    resolved = _result(
        TrustedCallerResolutionDisposition.RESOLVED,
        status=PlatformUserStatus.ACTIVE.value,
        caller=_caller(principal),
    )

    resolver = MagicMock()
    resolver.resolve.return_value = resolved
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is resolved
    acceptance.accept.assert_not_called()
    resolver.resolve.assert_called_once_with(
        organization_id=ORG,
        principal=principal,
    )


def test_invited_result_accepts_then_requires_active_resolution():
    principal = _principal()

    invited = _result(
        TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
        status=PlatformUserStatus.INVITED.value,
    )

    resolved = _result(
        TrustedCallerResolutionDisposition.RESOLVED,
        status=PlatformUserStatus.ACTIVE.value,
        caller=_caller(principal),
    )

    resolver = MagicMock()
    resolver.resolve.side_effect = [
        invited,
        resolved,
    ]
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is resolved

    acceptance.accept.assert_called_once_with(
        organization_id=ORG,
        principal=principal,
    )

    assert resolver.resolve.call_count == 2


@pytest.mark.parametrize(
    "disposition,status",
    [
        (
            TrustedCallerResolutionDisposition.NO_MATCH,
            None,
        ),
        (
            TrustedCallerResolutionDisposition.PLATFORM_USER_INACTIVE,
            PlatformUserStatus.INVITED.value,
        ),
        (
            TrustedCallerResolutionDisposition.ISSUER_MISMATCH,
            PlatformUserStatus.ACTIVE.value,
        ),
        (
            TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
            PlatformUserStatus.SUSPENDED.value,
        ),
        (
            TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
            PlatformUserStatus.DISABLED.value,
        ),
    ],
)
def test_non_invited_results_do_not_trigger_acceptance(
    disposition,
    status,
):
    principal = _principal()

    original = _result(
        disposition,
        status=status,
    )

    resolver = MagicMock()
    resolver.resolve.return_value = original
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is original
    acceptance.accept.assert_not_called()
    resolver.resolve.assert_called_once()


def test_invited_decision_uses_structured_status_not_evidence():
    principal = _principal()

    invited = TrustedCallerResolutionResult(
        disposition=(
            TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE
        ),
        organization_id=ORG,
        reason="test",
        platform_user_id="user-a",
        platform_user_status=PlatformUserStatus.INVITED.value,
        evidence=("diagnostic-text-can-change",),
    )

    resolved = _result(
        TrustedCallerResolutionDisposition.RESOLVED,
        status=PlatformUserStatus.ACTIVE.value,
        caller=_caller(principal),
    )

    resolver = MagicMock()
    resolver.resolve.side_effect = [
        invited,
        resolved,
    ]
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is resolved
    acceptance.accept.assert_called_once()


def test_evidence_string_cannot_fake_invited_status():
    principal = _principal()

    suspended = TrustedCallerResolutionResult(
        disposition=(
            TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE
        ),
        organization_id=ORG,
        reason="test",
        platform_user_id="user-a",
        platform_user_status=PlatformUserStatus.SUSPENDED.value,
        evidence=("status=Invited",),
    )

    resolver = MagicMock()
    resolver.resolve.return_value = suspended
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is suspended
    acceptance.accept.assert_not_called()


def test_post_acceptance_must_resolve_active_caller():
    principal = _principal()

    invited = _result(
        TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
        status=PlatformUserStatus.INVITED.value,
    )

    still_invited = _result(
        TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
        status=PlatformUserStatus.INVITED.value,
    )

    resolver = MagicMock()
    resolver.resolve.side_effect = [
        invited,
        still_invited,
    ]
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    with pytest.raises(
        PlatformAuthenticationCompositionError
    ):
        service.resolve_or_accept_invitation(
            organization_id=ORG,
            principal=principal,
        )

    acceptance.accept.assert_called_once()


def test_requires_trusted_external_principal():
    resolver = MagicMock()
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    with pytest.raises(
        TypeError,
        match="TrustedExternalPrincipal",
    ):
        service.resolve_or_accept_invitation(
            organization_id=ORG,
            principal=object(),
        )

    resolver.resolve.assert_not_called()
    acceptance.accept.assert_not_called()
