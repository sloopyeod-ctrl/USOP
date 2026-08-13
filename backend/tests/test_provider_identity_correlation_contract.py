import pytest

from app.connectors.provider.ProviderIdentityCorrelationContract import (
    ProviderIdentityCorrelationContract,
)


def test_contract_accepts_canonical_provider():
    contract = ProviderIdentityCorrelationContract(
        provider_name="microsoft-entra",
        account_source_system="Microsoft Entra ID",
        subject_semantics="Graph object id",
        tenant_semantics="Tenant id",
    )
    assert contract.provider_name == "microsoft-entra"


@pytest.mark.parametrize(
    "provider_name",
    ["", "Microsoft Entra", "-entra", "entra-", "entra--id"],
)
def test_contract_rejects_invalid_provider(provider_name):
    with pytest.raises(ValueError):
        ProviderIdentityCorrelationContract(
            provider_name=provider_name,
            account_source_system="Source",
            subject_semantics="Subject",
            tenant_semantics="Tenant",
        )
