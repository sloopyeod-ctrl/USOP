import hmac
from dataclasses import dataclass

from app.schemas.license import LicenseInstallRequest
from app.security.license_signature_verifier import (
    LicenseSignatureVerificationError,
    LicenseSignatureVerifier,
)
from app.services.license_canonicalization import (
    LicenseCanonicalizationError,
    canonicalize_license_payload,
    hash_canonical_license_payload,
)


class LicenseCryptographicValidationError(ValueError):
    """Base error for signed License validation failures."""


class LicensePayloadHashMismatchError(
    LicenseCryptographicValidationError
):
    """Raised when the declared License payload hash is incorrect."""


class LicensePayloadCanonicalizationError(
    LicenseCryptographicValidationError
):
    """Raised when the declared License payload cannot be canonicalized."""


class LicensePayloadSignatureError(
    LicenseCryptographicValidationError
):
    """Raised when signed License verification fails."""


@dataclass(frozen=True)
class LicenseCryptographicValidationResult:
    canonical_payload_hash: str
    signing_key_identifier: str
    algorithm: str


class LicenseCryptographicValidator:
    """
    Validate the cryptographic integrity of a signed License envelope.

    This service proves that:

    - canonical_payload can be deterministically serialized;
    - canonical_payload_hash matches the serialized payload;
    - signature verifies over those exact canonical bytes;
    - signing_key_identifier resolves to trusted verification material.

    It does not determine commercial effectiveness, expiration, seats,
    Organization binding, Deployment binding, or Subscription State.
    """

    def __init__(
        self,
        signature_verifier: LicenseSignatureVerifier,
    ) -> None:
        self.signature_verifier = signature_verifier

    def validate(
        self,
        request: LicenseInstallRequest,
    ) -> LicenseCryptographicValidationResult:
        try:
            canonical_bytes = canonicalize_license_payload(
                request.canonical_payload
            )

            calculated_hash = hash_canonical_license_payload(
                request.canonical_payload
            )

        except LicenseCanonicalizationError as error:
            raise LicensePayloadCanonicalizationError(
                "License canonical payload is invalid."
            ) from error

        declared_hash = (
            request.canonical_payload_hash
            .strip()
            .lower()
        )

        if not hmac.compare_digest(
            calculated_hash,
            declared_hash,
        ):
            raise LicensePayloadHashMismatchError(
                "License canonical payload hash does not match."
            )

        try:
            verification = self.signature_verifier.verify(
                canonical_payload=canonical_bytes,
                signature=request.signature,
                signing_key_identifier=(
                    request.signing_key_identifier
                ),
            )

        except LicenseSignatureVerificationError as error:
            raise LicensePayloadSignatureError(
                "License cryptographic signature validation failed."
            ) from error

        return LicenseCryptographicValidationResult(
            canonical_payload_hash=calculated_hash,
            signing_key_identifier=(
                verification.signing_key_identifier
            ),
            algorithm=verification.algorithm,
        )
