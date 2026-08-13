from app.connectors.provider.ProviderIdentityCorrelationContract import (
    ProviderIdentityCorrelationContract,
)


ENTRA_IDENTITY_CORRELATION_CONTRACT = (
    ProviderIdentityCorrelationContract(
        provider_name="microsoft-entra",
        account_source_system="Microsoft Entra ID",
        subject_semantics="Microsoft Graph user object id",
        tenant_semantics="Microsoft Entra tenant id",
        supports_deterministic_subject_match=True,
    )
)
