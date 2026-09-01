import pytest

from cryptography.hazmat.primitives.asymmetric import (
    ec,
    rsa,
)
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from license_authority.signing_key import (
    InvalidLicenseAuthorityPrivateKeyError,
    InvalidLicenseAuthoritySigningKeyIdentifierError,
    LicenseAuthoritySigningKey,
    UnsupportedLicenseAuthorityPrivateKeyError,
    load_license_authority_signing_key,
)


def _private_pem(private_key) -> bytes:
    return private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )


def test_loads_valid_p256_private_signing_key():
    private_key = ec.generate_private_key(ec.SECP256R1())

    loaded = load_license_authority_signing_key(
        key_identifier="usop-license-2026-01",
        private_key_pem=_private_pem(private_key),
    )

    assert isinstance(loaded, LicenseAuthoritySigningKey)
    assert loaded.key_identifier == "usop-license-2026-01"
    assert isinstance(
        loaded.private_key,
        ec.EllipticCurvePrivateKey,
    )
    assert isinstance(
        loaded.private_key.curve,
        ec.SECP256R1,
    )


def test_normalizes_signing_key_identifier():
    private_key = ec.generate_private_key(ec.SECP256R1())

    loaded = load_license_authority_signing_key(
        key_identifier="  usop-license-2026-01  ",
        private_key_pem=_private_pem(private_key),
    )

    assert loaded.key_identifier == "usop-license-2026-01"


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        "\t",
        "\n",
    ],
)
def test_rejects_empty_signing_key_identifier(identifier):
    private_key = ec.generate_private_key(ec.SECP256R1())

    with pytest.raises(
        InvalidLicenseAuthoritySigningKeyIdentifierError
    ):
        load_license_authority_signing_key(
            key_identifier=identifier,
            private_key_pem=_private_pem(private_key),
        )


def test_rejects_non_string_signing_key_identifier():
    private_key = ec.generate_private_key(ec.SECP256R1())

    with pytest.raises(
        InvalidLicenseAuthoritySigningKeyIdentifierError
    ):
        load_license_authority_signing_key(
            key_identifier=123,
            private_key_pem=_private_pem(private_key),
        )


@pytest.mark.parametrize(
    "private_key_pem",
    [
        b"",
        b" ",
        b"\n",
    ],
)
def test_rejects_empty_private_key_material(private_key_pem):
    with pytest.raises(
        InvalidLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=private_key_pem,
        )


def test_rejects_non_bytes_private_key_material():
    with pytest.raises(
        InvalidLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem="not-bytes",
        )


def test_rejects_malformed_private_key_pem():
    with pytest.raises(
        InvalidLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=(
                b"-----BEGIN PRIVATE KEY-----\n"
                b"not-a-real-key\n"
                b"-----END PRIVATE KEY-----\n"
            ),
        )


def test_rejects_public_key_material():
    private_key = ec.generate_private_key(ec.SECP256R1())

    public_pem = (
        private_key
        .public_key()
        .public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo,
        )
    )

    with pytest.raises(
        InvalidLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=public_pem,
        )


def test_rejects_rsa_private_key():
    rsa_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with pytest.raises(
        UnsupportedLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=_private_pem(rsa_private_key),
        )


def test_rejects_wrong_ec_curve():
    private_key = ec.generate_private_key(ec.SECP384R1())

    with pytest.raises(
        UnsupportedLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=_private_pem(private_key),
        )


def test_rejects_encrypted_private_key_without_password_support():
    private_key = ec.generate_private_key(ec.SECP256R1())

    encrypted_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=BestAvailableEncryption(
            b"test-only-password"
        ),
    )

    with pytest.raises(
        InvalidLicenseAuthorityPrivateKeyError
    ):
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=encrypted_pem,
        )


def test_repr_redacts_private_key():
    private_key = ec.generate_private_key(ec.SECP256R1())
    pem = _private_pem(private_key)

    loaded = load_license_authority_signing_key(
        key_identifier="test-key",
        private_key_pem=pem,
    )

    rendered = repr(loaded)

    assert "private_key=<redacted>" in rendered
    assert "BEGIN PRIVATE KEY" not in rendered
    assert pem.decode() not in rendered


def test_returned_authority_does_not_retain_original_pem():
    private_key = ec.generate_private_key(ec.SECP256R1())
    pem = _private_pem(private_key)

    loaded = load_license_authority_signing_key(
        key_identifier="test-key",
        private_key_pem=pem,
    )

    assert not hasattr(loaded, "private_key_pem")
    assert not hasattr(loaded, "pem")


def test_error_does_not_disclose_private_key_material():
    secret_marker = (
        b"USOP-PRIVATE-MATERIAL-MUST-NOT-LEAK"
    )

    malformed = (
        b"-----BEGIN PRIVATE KEY-----\n"
        + secret_marker
        + b"\n-----END PRIVATE KEY-----\n"
    )

    with pytest.raises(
        InvalidLicenseAuthorityPrivateKeyError
    ) as exc_info:
        load_license_authority_signing_key(
            key_identifier="test-key",
            private_key_pem=malformed,
        )

    rendered = str(exc_info.value)

    assert secret_marker.decode() not in rendered
    assert "BEGIN PRIVATE KEY" not in rendered
