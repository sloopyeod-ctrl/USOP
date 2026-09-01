import base64
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.schemas.license import LicenseInstallRequest
from app.security.license_signature_verifier import (
    LicenseSignatureVerifier,
)
from app.security.license_signing_keys import (
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
)
from app.services.license_canonicalization import (
    canonicalize_license_payload,
    hash_canonical_license_payload,
)
from app.services.license_cryptographic_validator import (
    LicenseCryptographicValidator,
    LicensePayloadHashMismatchError,
    LicensePayloadSignatureError,
)


KEY_IDENTIFIER = "usop-license-root-test-01"


def build_fixture():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )

    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier=KEY_IDENTIFIER,
                public_key_pem=public_pem,
            )
        ]
    )

    verifier = LicenseSignatureVerifier(
        registry
    )

    validator = LicenseCryptographicValidator(
        verifier
    )

    return private_key, validator


def build_request(
    private_key,
    *,
    canonical_payload=None,
    canonical_payload_hash=None,
    signing_key_identifier=KEY_IDENTIFIER,
):
    payload = canonical_payload or {
        "organization_id": (
            "00000000-0000-0000-0000-000000000001"
        ),
        "commercial_edition": "Enterprise",
        "commercial_purpose": "Beta",
        "seat_limit": 25,
    }

    canonical_bytes = canonicalize_license_payload(
        payload
    )

    signature = private_key.sign(
        canonical_bytes,
        ec.ECDSA(
            hashes.SHA256()
        ),
    )

    now = datetime.now(
        timezone.utc
    )

    return LicenseInstallRequest(
        organization_id=(
            "00000000-0000-0000-0000-000000000001"
        ),
        license_identifier="license-test-001",
        commercial_edition=(
            CommercialEdition.ENTERPRISE
        ),
        commercial_purpose=(
            CommercialPurpose.BETA
        ),
        license_format_version="1",
        issued_at=now,
        effective_at=now,
        expires_at=(
            now + timedelta(days=90)
        ),
        deployment_identifier=None,
        seat_limit=25,
        commercial_modules=[
            "identity",
        ],
        feature_entitlements=[
            "identity.core",
        ],
        canonical_payload=payload,
        canonical_payload_hash=(
            canonical_payload_hash
            or hash_canonical_license_payload(
                payload
            )
        ),
        signature=base64.b64encode(
            signature
        ).decode("ascii"),
        signing_key_identifier=(
            signing_key_identifier
        ),
    )


def test_valid_signed_license_envelope_passes():
    private_key, validator = (
        build_fixture()
    )

    request = build_request(
        private_key
    )

    result = validator.validate(
        request
    )

    assert result.canonical_payload_hash == (
        request.canonical_payload_hash
    )

    assert result.signing_key_identifier == (
        KEY_IDENTIFIER
    )

    assert result.algorithm == (
        "ECDSA-P256-SHA256"
    )


def test_declared_hash_mismatch_fails_closed():
    private_key, validator = (
        build_fixture()
    )

    request = build_request(
        private_key,
        canonical_payload_hash=("0" * 64),
    )

    with pytest.raises(
        LicensePayloadHashMismatchError,
    ):
        validator.validate(
            request
        )


def test_payload_modified_after_signing_fails_closed():
    private_key, validator = (
        build_fixture()
    )

    original = {
        "seat_limit": 25,
    }

    request = build_request(
        private_key,
        canonical_payload=original,
    )

    tampered_payload = {
        "seat_limit": 250,
    }

    tampered = request.model_copy(
        update={
            "canonical_payload": tampered_payload,
            "canonical_payload_hash": (
                hash_canonical_license_payload(
                    tampered_payload
                )
            ),
        }
    )

    with pytest.raises(
        LicensePayloadSignatureError,
    ):
        validator.validate(
            tampered
        )


def test_signature_modified_fails_closed():
    private_key, validator = (
        build_fixture()
    )

    request = build_request(
        private_key
    )

    tampered = request.model_copy(
        update={
            "signature": base64.b64encode(
                b"invalid-signature"
            ).decode("ascii")
        }
    )

    with pytest.raises(
        LicensePayloadSignatureError,
    ):
        validator.validate(
            tampered
        )


def test_unknown_signing_key_fails_closed():
    private_key, validator = (
        build_fixture()
    )

    request = build_request(
        private_key,
        signing_key_identifier=(
            "unknown-license-key"
        ),
    )

    with pytest.raises(
        LicensePayloadSignatureError,
    ):
        validator.validate(
            request
        )


def test_uppercase_declared_hash_is_accepted():
    private_key, validator = (
        build_fixture()
    )

    request = build_request(
        private_key
    )

    uppercase = request.model_copy(
        update={
            "canonical_payload_hash": (
                request
                .canonical_payload_hash
                .upper()
            )
        }
    )

    result = validator.validate(
        uppercase
    )

    assert result.canonical_payload_hash == (
        request.canonical_payload_hash
    )
