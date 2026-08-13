from datetime import UTC, datetime

import pytest

from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


def test_trusted_external_principal_normalizes_provider():
    principal = TrustedExternalPrincipal(
        identity_provider="microsoft-entra",
        external_tenant_id="tenant-42",
        external_subject_id="subject-42",
        issuer="https://issuer.example/",
        authenticated_at=datetime(
            2026,
            8,
            13,
            12,
            0,
            tzinfo=UTC,
        ),
    )

    assert principal.identity_provider == "microsoft-entra"
    assert principal.external_tenant_id == "tenant-42"
    assert principal.external_subject_id == "subject-42"


@pytest.mark.parametrize(
    "provider_name",
    ["", "Microsoft Entra", "-entra", "entra-", "entra--id"],
)
def test_trusted_external_principal_rejects_bad_provider(
    provider_name,
):
    with pytest.raises(ValueError):
        TrustedExternalPrincipal(
            identity_provider=provider_name,
            external_tenant_id="tenant",
            external_subject_id="subject",
        )
