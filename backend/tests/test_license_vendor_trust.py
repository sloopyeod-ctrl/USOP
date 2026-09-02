import os

from app.security.license_vendor_trust import (
    VENDOR_TRUSTED_LICENSE_SIGNING_KEYS,
    build_vendor_license_signing_key_registry,
)


def test_vendor_trust_is_intentionally_empty_before_provisioning():
    assert VENDOR_TRUSTED_LICENSE_SIGNING_KEYS == ()

    registry = build_vendor_license_signing_key_registry()

    assert registry.identifiers() == ()


def test_each_vendor_registry_is_independently_built():
    first = build_vendor_license_signing_key_registry()
    second = build_vendor_license_signing_key_registry()

    assert first is not second

    assert first.identifiers() == ()
    assert second.identifiers() == ()


def test_environment_variable_cannot_inject_vendor_trust(
    monkeypatch,
):
    monkeypatch.setenv(
        "USOP_LICENSE_SIGNING_KEY",
        "attacker-controlled",
    )

    monkeypatch.setenv(
        "USOP_LICENSE_PUBLIC_KEY",
        "attacker-controlled",
    )

    monkeypatch.setenv(
        "USOP_LICENSE_TRUST_ROOT",
        "attacker-controlled",
    )

    registry = build_vendor_license_signing_key_registry()

    assert registry.identifiers() == ()


def test_vendor_trust_provider_does_not_depend_on_environment():
    before = dict(os.environ)

    registry = build_vendor_license_signing_key_registry()

    after = dict(os.environ)

    assert before == after
    assert registry.identifiers() == ()


def test_returned_registry_exposes_no_trust_mutation_api():
    registry = build_vendor_license_signing_key_registry()

    assert not hasattr(registry, "register")
    assert not hasattr(registry, "add")
    assert not hasattr(registry, "append")
    assert not hasattr(registry, "update")
    assert not hasattr(registry, "remove")

def test_license_api_composition_uses_vendor_trust_provider():
    from app.api.v1.licenses import (
        get_license_cryptographic_validator,
    )

    validator = get_license_cryptographic_validator()

    registry = (
        validator
        .signature_verifier
        .registry
    )

    assert registry.identifiers() == ()

def test_default_runtime_rejects_arbitrary_valid_vendor_signature():
    from datetime import UTC, datetime, timedelta

    import pytest

    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
    )

    from app.api.v1.licenses import (
        get_license_cryptographic_validator,
    )
    from app.domain.commercial_edition import CommercialEdition
    from app.domain.commercial_purpose import CommercialPurpose
    from app.services.license_cryptographic_validator import (
        LicensePayloadSignatureError,
    )
    from license_authority.issuance import (
        LicenseIssuanceRequest,
        LicenseIssuanceService,
    )
    from license_authority.signing_key import (
        load_license_authority_signing_key,
    )

    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    authority_key = load_license_authority_signing_key(
        key_identifier="arbitrary-untrusted-key",
        private_key_pem=private_pem,
    )

    now = datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        LicenseIssuanceRequest(
            organization_id=(
                "00000000-0000-0000-0000-000000000001"
            ),
            commercial_edition=(
                CommercialEdition.ENTERPRISE
            ),
            commercial_purpose=(
                CommercialPurpose.BETA
            ),
            issued_at=now,
            effective_at=now,
            expires_at=(
                now + timedelta(days=90)
            ),
            deployment_identifier=None,
            seat_limit=10,
            commercial_modules=(),
            feature_entitlements=(),
        )
    )

    validator = (
        get_license_cryptographic_validator()
    )

    assert (
        validator
        .signature_verifier
        .registry
        .identifiers()
    ) == ()

    with pytest.raises(
        LicensePayloadSignatureError
    ):
        validator.validate(
            issued
        )
