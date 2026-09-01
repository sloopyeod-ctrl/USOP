import base64
import binascii
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
)

from app.security.license_signing_keys import (
    TrustedLicenseSigningKeyRegistry,
    UnknownLicenseSigningKeyError,
)


class LicenseSignatureVerificationError(ValueError):
    """Base error for License cryptographic verification failures."""


class InvalidLicenseSignatureEncodingError(
    LicenseSignatureVerificationError
):
    """Raised when the supplied License signature is not valid Base64."""


class InvalidLicensePublicKeyError(
    LicenseSignatureVerificationError
):
    """Raised when trusted public-key material cannot be used for License verification."""


class UnsupportedLicensePublicKeyError(
    LicenseSignatureVerificationError
):
    """Raised when a trusted key is not an ECDSA P-256 public key."""


class LicenseSignatureMismatchError(
    LicenseSignatureVerificationError
):
    """Raised when a License signature does not verify."""


class UntrustedLicenseSigningKeyError(
    LicenseSignatureVerificationError
):
    """Raised when a License references an unknown signing key."""


@dataclass(frozen=True)
class LicenseSignatureVerificationResult:
    signing_key_identifier: str
    algorithm: str = "ECDSA-P256-SHA256"


class LicenseSignatureVerifier:
    """
    Verify signed License canonical bytes using trusted public material.

    Verification contract:

    - signing-key identifiers must resolve through the trusted registry;
    - public keys must be PEM-encoded EC keys;
    - the permitted curve is NIST P-256 / secp256r1 only;
    - signatures are Base64-encoded ASN.1 DER ECDSA signatures;
    - signatures are verified using ECDSA with SHA-256;
    - all malformed, unsupported, unknown, or invalid inputs fail closed.
    """

    def __init__(
        self,
        registry: TrustedLicenseSigningKeyRegistry,
    ) -> None:
        self.registry = registry

    def verify(
        self,
        *,
        canonical_payload: bytes,
        signature: str,
        signing_key_identifier: str,
    ) -> LicenseSignatureVerificationResult:
        if not isinstance(canonical_payload, bytes):
            raise LicenseSignatureVerificationError(
                "License canonical payload must be bytes."
            )

        if not canonical_payload:
            raise LicenseSignatureVerificationError(
                "License canonical payload must not be empty."
            )

        if not isinstance(signature, str):
            raise InvalidLicenseSignatureEncodingError(
                "License signature must be a Base64 string."
            )

        normalized_signature = signature.strip()

        if not normalized_signature:
            raise InvalidLicenseSignatureEncodingError(
                "License signature must not be empty."
            )

        try:
            trusted_key = self.registry.resolve(
                signing_key_identifier
            )
        except UnknownLicenseSigningKeyError as error:
            raise UntrustedLicenseSigningKeyError(
                "License signing key is not trusted."
            ) from error

        try:
            public_key = load_pem_public_key(
                trusted_key.public_key_pem
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise InvalidLicensePublicKeyError(
                "Trusted License public key is invalid PEM."
            ) from error

        if not isinstance(
            public_key,
            ec.EllipticCurvePublicKey,
        ):
            raise UnsupportedLicensePublicKeyError(
                "License verification requires an EC public key."
            )

        if not isinstance(
            public_key.curve,
            ec.SECP256R1,
        ):
            raise UnsupportedLicensePublicKeyError(
                "License verification requires the P-256 curve."
            )

        try:
            signature_bytes = base64.b64decode(
                normalized_signature,
                validate=True,
            )
        except (
            binascii.Error,
            ValueError,
        ) as error:
            raise InvalidLicenseSignatureEncodingError(
                "License signature is not valid Base64."
            ) from error

        if not signature_bytes:
            raise InvalidLicenseSignatureEncodingError(
                "License signature decoded to empty data."
            )

        try:
            public_key.verify(
                signature_bytes,
                canonical_payload,
                ec.ECDSA(
                    hashes.SHA256()
                ),
            )
        except InvalidSignature as error:
            raise LicenseSignatureMismatchError(
                "License signature verification failed."
            ) from error

        return LicenseSignatureVerificationResult(
            signing_key_identifier=(
                trusted_key.key_identifier
            ),
        )
