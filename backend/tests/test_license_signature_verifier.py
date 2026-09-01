import base64

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import (
    ec,
    rsa,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from app.security.license_signature_verifier import (
    InvalidLicensePublicKeyError,
    InvalidLicenseSignatureEncodingError,
    LicenseSignatureMismatchError,
    LicenseSignatureVerificationError,
    LicenseSignatureVerifier,
    UnsupportedLicensePublicKeyError,
    UntrustedLicenseSigningKeyError,
)
from app.security.license_signing_keys import (
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
)
from app.services.license_canonicalization import (
    canonicalize_license_payload,
)


KEY_IDENTIFIER = "usop-license-root-test-01"


def public_pem(public_key) -> bytes:
    return public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )


def build_verifier(public_key) -> LicenseSignatureVerifier:
    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier=KEY_IDENTIFIER,
                public_key_pem=public_pem(
                    public_key
                ),
            )
        ]
    )

    return LicenseSignatureVerifier(
        registry
    )


def sign_payload(
    private_key: ec.EllipticCurvePrivateKey,
    payload: bytes,
) -> str:
    signature = private_key.sign(
        payload,
        ec.ECDSA(
            hashes.SHA256()
        ),
    )

    return base64.b64encode(
        signature
    ).decode("ascii")


def test_valid_p256_signature_verifies():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    payload = canonicalize_license_payload(
        {
            "organization_id": "org-1",
            "commercial_edition": "Enterprise",
        }
    )

    signature = sign_payload(
        private_key,
        payload,
    )

    result = build_verifier(
        private_key.public_key()
    ).verify(
        canonical_payload=payload,
        signature=signature,
        signing_key_identifier=KEY_IDENTIFIER,
    )

    assert result.signing_key_identifier == (
        KEY_IDENTIFIER
    )
    assert result.algorithm == (
        "ECDSA-P256-SHA256"
    )


def test_modified_payload_fails_closed():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    original = canonicalize_license_payload(
        {
            "seat_limit": 25,
        }
    )

    modified = canonicalize_license_payload(
        {
            "seat_limit": 250,
        }
    )

    signature = sign_payload(
        private_key,
        original,
    )

    with pytest.raises(
        LicenseSignatureMismatchError,
    ):
        build_verifier(
            private_key.public_key()
        ).verify(
            canonical_payload=modified,
            signature=signature,
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_wrong_public_key_fails_closed():
    signing_private_key = (
        ec.generate_private_key(
            ec.SECP256R1()
        )
    )

    wrong_private_key = (
        ec.generate_private_key(
            ec.SECP256R1()
        )
    )

    payload = canonicalize_license_payload(
        {
            "organization_id": "org-1",
        }
    )

    signature = sign_payload(
        signing_private_key,
        payload,
    )

    with pytest.raises(
        LicenseSignatureMismatchError,
    ):
        build_verifier(
            wrong_private_key.public_key()
        ).verify(
            canonical_payload=payload,
            signature=signature,
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_malformed_base64_signature_fails_closed():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    verifier = build_verifier(
        private_key.public_key()
    )

    with pytest.raises(
        InvalidLicenseSignatureEncodingError,
    ):
        verifier.verify(
            canonical_payload=b'{"a":1}',
            signature="%%%not-base64%%%",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_empty_signature_fails_closed():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    verifier = build_verifier(
        private_key.public_key()
    )

    with pytest.raises(
        InvalidLicenseSignatureEncodingError,
    ):
        verifier.verify(
            canonical_payload=b'{"a":1}',
            signature="   ",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_malformed_pem_fails_closed():
    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier=KEY_IDENTIFIER,
                public_key_pem=(
                    b"not-a-valid-public-key"
                ),
            )
        ]
    )

    verifier = LicenseSignatureVerifier(
        registry
    )

    with pytest.raises(
        InvalidLicensePublicKeyError,
    ):
        verifier.verify(
            canonical_payload=b'{"a":1}',
            signature="YQ==",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_rsa_public_key_is_rejected():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    verifier = build_verifier(
        private_key.public_key()
    )

    with pytest.raises(
        UnsupportedLicensePublicKeyError,
    ):
        verifier.verify(
            canonical_payload=b'{"a":1}',
            signature="YQ==",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_non_p256_ec_key_is_rejected():
    private_key = ec.generate_private_key(
        ec.SECP384R1()
    )

    verifier = build_verifier(
        private_key.public_key()
    )

    with pytest.raises(
        UnsupportedLicensePublicKeyError,
    ):
        verifier.verify(
            canonical_payload=b'{"a":1}',
            signature="YQ==",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_unknown_signing_key_fails_closed():
    registry = TrustedLicenseSigningKeyRegistry()

    verifier = LicenseSignatureVerifier(
        registry
    )

    with pytest.raises(
        UntrustedLicenseSigningKeyError,
    ):
        verifier.verify(
            canonical_payload=b'{"a":1}',
            signature="YQ==",
            signing_key_identifier=(
                "unknown-key"
            ),
        )


def test_empty_canonical_payload_fails_closed():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    verifier = build_verifier(
        private_key.public_key()
    )

    with pytest.raises(
        LicenseSignatureVerificationError,
    ):
        verifier.verify(
            canonical_payload=b"",
            signature="YQ==",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_non_bytes_canonical_payload_fails_closed():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    verifier = build_verifier(
        private_key.public_key()
    )

    with pytest.raises(
        LicenseSignatureVerificationError,
    ):
        verifier.verify(
            canonical_payload="not-bytes",  # type: ignore[arg-type]
            signature="YQ==",
            signing_key_identifier=KEY_IDENTIFIER,
        )


def test_signature_transport_is_base64_encoded_der():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    payload = b'{"a":1}'

    encoded_signature = sign_payload(
        private_key,
        payload,
    )

    decoded_signature = base64.b64decode(
        encoded_signature,
        validate=True,
    )

    assert decoded_signature.startswith(
        b"\x30"
    )
