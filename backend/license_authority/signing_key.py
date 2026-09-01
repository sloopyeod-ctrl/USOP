from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
)


class LicenseAuthoritySigningKeyError(ValueError):
    """Base error for License Authority signing-key failures."""


class InvalidLicenseAuthoritySigningKeyIdentifierError(
    LicenseAuthoritySigningKeyError
):
    """Raised when the operator signing-key identifier is invalid."""


class InvalidLicenseAuthorityPrivateKeyError(
    LicenseAuthoritySigningKeyError
):
    """Raised when operator private-key material cannot be loaded."""


class UnsupportedLicenseAuthorityPrivateKeyError(
    LicenseAuthoritySigningKeyError
):
    """Raised when private-key material uses an unsupported algorithm."""


@dataclass(frozen=True)
class LicenseAuthoritySigningKey:
    """
    Validated operator-side License signing authority.

    The original PEM bytes are deliberately not retained by this object.
    """

    key_identifier: str
    private_key: ec.EllipticCurvePrivateKey

    def __repr__(self) -> str:
        return (
            "LicenseAuthoritySigningKey("
            f"key_identifier={self.key_identifier!r}, "
            "private_key=<redacted>"
            ")"
        )


def load_license_authority_signing_key(
    *,
    key_identifier: str,
    private_key_pem: bytes,
) -> LicenseAuthoritySigningKey:
    """
    Load and validate vendor/operator License signing material.

    Contract:

    - key_identifier must be a non-empty string;
    - private_key_pem must be non-empty bytes;
    - unencrypted PKCS#8 or traditional PEM private keys may be loaded;
    - the key must be an EC private key;
    - the permitted curve is P-256 / secp256r1 only;
    - malformed, public-only, encrypted, RSA, and unsupported EC keys fail closed;
    - raw PEM material is never retained in the returned authority object.
    """

    if not isinstance(key_identifier, str):
        raise InvalidLicenseAuthoritySigningKeyIdentifierError(
            "License Authority signing-key identifier must be a string."
        )

    normalized_identifier = key_identifier.strip()

    if not normalized_identifier:
        raise InvalidLicenseAuthoritySigningKeyIdentifierError(
            "License Authority signing-key identifier must not be empty."
        )

    if not isinstance(private_key_pem, bytes):
        raise InvalidLicenseAuthorityPrivateKeyError(
            "License Authority private signing key must be PEM bytes."
        )

    if not private_key_pem.strip():
        raise InvalidLicenseAuthorityPrivateKeyError(
            "License Authority private signing key must not be empty."
        )

    try:
        private_key = load_pem_private_key(
            private_key_pem,
            password=None,
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise InvalidLicenseAuthorityPrivateKeyError(
            "License Authority private signing key is invalid or unsupported PEM."
        ) from error

    if not isinstance(
        private_key,
        ec.EllipticCurvePrivateKey,
    ):
        raise UnsupportedLicenseAuthorityPrivateKeyError(
            "License Authority requires an EC private signing key."
        )

    if not isinstance(
        private_key.curve,
        ec.SECP256R1,
    ):
        raise UnsupportedLicenseAuthorityPrivateKeyError(
            "License Authority requires the P-256 curve."
        )

    return LicenseAuthoritySigningKey(
        key_identifier=normalized_identifier,
        private_key=private_key,
    )
