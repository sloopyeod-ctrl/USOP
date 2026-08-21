import inspect
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
    evidence=(),
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
        evidence=evidence,
    )


def _service(first_result, second_result=None):
    resolver = MagicMock()
    if second_result is None:
        resolver.resolve.return_value = first_result
    else:
        resolver.resolve.side_effect = [
            first_result,
            second_result,
        ]

    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    return service, resolver, acceptance


def test_gate_only_structured_invited_state_triggers_acceptance():
    principal = _principal()

    suspended = _result(
        TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
        status=PlatformUserStatus.SUSPENDED.value,
        evidence=("status=Invited",),
    )

    service, resolver, acceptance = _service(
        suspended
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is suspended
    acceptance.accept.assert_not_called()
    resolver.resolve.assert_called_once()


def test_gate_invited_status_requires_not_active_disposition():
    principal = _principal()

    fake_invited = _result(
        TrustedCallerResolutionDisposition.ISSUER_MISMATCH,
        status=PlatformUserStatus.INVITED.value,
    )

    service, _, acceptance = _service(
        fake_invited
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is fake_invited
    acceptance.accept.assert_not_called()


def test_gate_inactive_record_never_crosses_first_auth_boundary():
    principal = _principal()

    inactive = _result(
        TrustedCallerResolutionDisposition.PLATFORM_USER_INACTIVE,
        status=PlatformUserStatus.INVITED.value,
    )

    service, _, acceptance = _service(
        inactive
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is inactive
    acceptance.accept.assert_not_called()


def test_gate_no_match_never_creates_or_accepts_invitation():
    principal = _principal()

    no_match = _result(
        TrustedCallerResolutionDisposition.NO_MATCH,
        status=None,
    )

    service, _, acceptance = _service(
        no_match
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is no_match
    acceptance.accept.assert_not_called()


def test_gate_post_acceptance_resolution_must_be_resolved():
    principal = _principal()

    invited = _result(
        TrustedCallerResolutionDisposition.PLATFORM_USER_NOT_ACTIVE,
        status=PlatformUserStatus.INVITED.value,
    )

    issuer_mismatch = _result(
        TrustedCallerResolutionDisposition.ISSUER_MISMATCH,
        status=PlatformUserStatus.ACTIVE.value,
    )

    service, resolver, acceptance = _service(
        invited,
        issuer_mismatch,
    )

    with pytest.raises(
        PlatformAuthenticationCompositionError
    ):
        service.resolve_or_accept_invitation(
            organization_id=ORG,
            principal=principal,
        )

    acceptance.accept.assert_called_once_with(
        organization_id=ORG,
        principal=principal,
    )
    assert resolver.resolve.call_count == 2


def test_gate_resolved_result_must_contain_real_caller():
    principal = _principal()

    malformed = TrustedCallerResolutionResult(
        disposition=TrustedCallerResolutionDisposition.RESOLVED,
        organization_id=ORG,
        reason="malformed",
        platform_user_id="user-a",
        platform_user_status=PlatformUserStatus.ACTIVE.value,
        caller=None,
    )

    service, _, acceptance = _service(
        malformed
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result is malformed
    assert result.resolved is False
    acceptance.accept.assert_not_called()


def test_gate_post_acceptance_requires_real_trusted_platform_caller():
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

    service, _, acceptance = _service(
        invited,
        resolved,
    )

    result = service.resolve_or_accept_invitation(
        organization_id=ORG,
        principal=principal,
    )

    assert result.resolved is True
    assert isinstance(
        result.caller,
        TrustedPlatformCaller,
    )
    acceptance.accept.assert_called_once()


def test_gate_composition_does_not_validate_raw_credentials():
    source = inspect.getsource(
        PlatformAuthenticationCompositionService
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


def test_gate_composition_does_not_grant_runtime_authority():
    source = inspect.getsource(
        PlatformAuthenticationCompositionService
    )

    forbidden = (
        "PlatformRuntimeAuthorizationService",
        "PlatformAuthorizationService",
        "assign_role",
        "grant_permission",
        "LicenseRepository",
        "SeatRepository",
        "platform-administration.manage",
    )

    for token in forbidden:
        assert token not in source


def test_gate_composition_is_provider_neutral():
    source = inspect.getsource(
        PlatformAuthenticationCompositionService
    ).lower()

    forbidden = (
        "microsoft-entra",
        "okta",
        "google",
        "securew2",
    )

    for token in forbidden:
        assert token not in source


def test_gate_composition_does_not_parse_evidence_for_security_decision():
    source = inspect.getsource(
        PlatformAuthenticationCompositionService
    )

    assert "resolution.evidence" not in source
    assert "status=Invited" not in source


def test_gate_composition_does_not_mutate_platform_user_directly():
    source = inspect.getsource(
        PlatformAuthenticationCompositionService
    )

    forbidden = (
        ".status =",
        ".activated_at =",
        ".last_authenticated_at =",
        "record_first_authentication",
    )

    for token in forbidden:
        assert token not in source


def test_gate_requires_trusted_external_principal_before_resolution():
    resolver = MagicMock()
    acceptance = MagicMock()

    service = PlatformAuthenticationCompositionService(
        object(),
        trusted_caller_identity_service=resolver,
        invitation_acceptance_service=acceptance,
    )

    with pytest.raises(TypeError):
        service.resolve_or_accept_invitation(
            organization_id=ORG,
            principal=object(),
        )

    resolver.resolve.assert_not_called()
    acceptance.accept.assert_not_called()
