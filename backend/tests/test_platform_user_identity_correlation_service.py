from types import SimpleNamespace
from unittest.mock import MagicMock

from app.connectors.provider.ProviderIdentityCorrelationContract import (
    ProviderIdentityCorrelationContract,
)
from app.services.platform_user_identity_correlation_result import (
    PlatformUserIdentityCorrelationDisposition,
)
from app.services.platform_user_identity_correlation_service import (
    PlatformUserIdentityCorrelationService,
)


ORG = "org-42"
USER = "user-42"


def contract():
    return ProviderIdentityCorrelationContract(
        provider_name="microsoft-entra",
        account_source_system="Microsoft Entra ID",
        subject_semantics="Graph object id",
        tenant_semantics="Tenant id",
    )


def user(**overrides):
    values = dict(
        id=USER,
        organization_id=ORG,
        organizational_identity_id=None,
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-42",
        external_subject_id="subject-42",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def account(**overrides):
    values = dict(
        id="account-42",
        organizational_identity_id="oi-42",
        identity_id="identity-42",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def build(platform_user, accounts, provider_contract):
    db = MagicMock()
    platform_repo = MagicMock()
    account_repo = MagicMock()
    registry = MagicMock()

    platform_repo.get_by_id.return_value = platform_user
    account_repo.list_by_source_for_organization.return_value = accounts
    registry.get.return_value = provider_contract

    service = PlatformUserIdentityCorrelationService(
        db,
        provider_registry=registry,
        platform_user_repository=platform_repo,
        account_repository=account_repo,
    )
    return service, account_repo


def test_deterministic_match_is_candidate_only():
    service, account_repo = build(
        user(),
        [account()],
        contract(),
    )

    result = service.evaluate(
        organization_id=ORG,
        platform_user_id=USER,
    )

    assert result.disposition == (
        PlatformUserIdentityCorrelationDisposition.DETERMINISTIC_MATCH
    )
    assert result.organizational_identity_id == "oi-42"
    account_repo.list_by_source_for_organization.assert_called_once_with(
        organization_id=ORG,
        source_system="Microsoft Entra ID",
        source_identifier="subject-42",
    )


def test_missing_subject_fails_closed():
    service, account_repo = build(
        user(external_subject_id=None),
        [],
        contract(),
    )
    result = service.evaluate(
        organization_id=ORG,
        platform_user_id=USER,
    )
    assert result.disposition == (
        PlatformUserIdentityCorrelationDisposition.INSUFFICIENT_EVIDENCE
    )
    account_repo.list_by_source_for_organization.assert_not_called()


def test_unsupported_provider_does_not_fallback():
    service, account_repo = build(user(), [], None)
    result = service.evaluate(
        organization_id=ORG,
        platform_user_id=USER,
    )
    assert result.disposition == (
        PlatformUserIdentityCorrelationDisposition.UNSUPPORTED_PROVIDER
    )
    account_repo.list_by_source_for_organization.assert_not_called()


def test_multiple_matches_are_ambiguous():
    service, _ = build(
        user(),
        [account(id="a1"), account(id="a2")],
        contract(),
    )
    result = service.evaluate(
        organization_id=ORG,
        platform_user_id=USER,
    )
    assert result.disposition == (
        PlatformUserIdentityCorrelationDisposition.AMBIGUOUS
    )
    assert result.organizational_identity_id is None


def test_existing_binding_is_not_replaced():
    service, account_repo = build(
        user(organizational_identity_id="existing-oi"),
        [account()],
        contract(),
    )
    result = service.evaluate(
        organization_id=ORG,
        platform_user_id=USER,
    )
    assert result.disposition == (
        PlatformUserIdentityCorrelationDisposition.ALREADY_BOUND
    )
    account_repo.list_by_source_for_organization.assert_not_called()


def test_foreign_platform_user_is_not_visible():
    service, account_repo = build(
        user(organization_id="org-92"),
        [],
        contract(),
    )
    result = service.evaluate(
        organization_id=ORG,
        platform_user_id=USER,
    )
    assert result.disposition == (
        PlatformUserIdentityCorrelationDisposition.NO_MATCH
    )
    account_repo.list_by_source_for_organization.assert_not_called()
