from app.connectors.provider.ProviderIdentityCorrelationRegistry import (
    build_default_identity_correlation_registry,
)


def test_default_registry_exposes_entra_contract():
    registry = build_default_identity_correlation_registry()
    contract = registry.get(" MICROSOFT-ENTRA ")

    assert contract is not None
    assert contract.account_source_system == "Microsoft Entra ID"
    assert contract.supports_deterministic_subject_match is True
