import base64
import uuid
from dataclasses import dataclass
from datetime import datetime

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.schemas.license import LicenseInstallRequest
from app.services.license_canonicalization import (
    canonicalize_license_payload,
    hash_canonical_license_payload,
)

from license_authority.signing_key import (
    LicenseAuthoritySigningKey,
)


LICENSE_FORMAT_VERSION = "1.0"
LICENSE_IDENTIFIER_PREFIX = "USOP-LIC-"


class LicenseIssuanceError(ValueError):
    """Base error for License Authority issuance failures."""


@dataclass(frozen=True)
class LicenseIssuanceRequest:
    """
    Operator-controlled commercial inputs for one immutable License.
    """

    organization_id: str
    commercial_edition: CommercialEdition
    commercial_purpose: CommercialPurpose
    issued_at: datetime
    effective_at: datetime
    expires_at: datetime | None = None
    deployment_identifier: str | None = None
    seat_limit: int | None = None
    commercial_modules: tuple[str, ...] = ()
    feature_entitlements: tuple[str, ...] = ()


class LicenseIssuanceService:
    """
    Vendor/operator authority for creating signed License envelopes.

    This service performs no persistence and is not customer runtime logic.
    """

    def __init__(
        self,
        signing_key: LicenseAuthoritySigningKey,
    ) -> None:
        self.signing_key = signing_key

    def issue(
        self,
        request: LicenseIssuanceRequest,
    ) -> LicenseInstallRequest:
        if not isinstance(request.organization_id, str):
            raise LicenseIssuanceError(
                "License organization_id must be a string."
            )

        organization_id = request.organization_id.strip()

        if not organization_id:
            raise LicenseIssuanceError(
                "License organization_id must not be empty."
            )

        if not isinstance(
            request.commercial_edition,
            CommercialEdition,
        ):
            raise LicenseIssuanceError(
                "License commercial_edition must use canonical vocabulary."
            )

        if not isinstance(
            request.commercial_purpose,
            CommercialPurpose,
        ):
            raise LicenseIssuanceError(
                "License commercial_purpose must use canonical vocabulary."
            )

        for field_name, value in (
            ("issued_at", request.issued_at),
            ("effective_at", request.effective_at),
            ("expires_at", request.expires_at),
        ):
            if value is None and field_name == "expires_at":
                continue

            if not isinstance(value, datetime):
                raise LicenseIssuanceError(
                    f"License {field_name} must be a datetime."
                )

            if (
                value.tzinfo is None
                or value.utcoffset() is None
            ):
                raise LicenseIssuanceError(
                    f"License {field_name} must be timezone-aware."
                )

        if (
            request.expires_at is not None
            and request.expires_at <= request.effective_at
        ):
            raise LicenseIssuanceError(
                "License expiration must occur after its effective date."
            )

        if (
            request.seat_limit is not None
            and request.seat_limit < 1
        ):
            raise LicenseIssuanceError(
                "License seat limit must be at least 1."
            )

        license_identifier = (
            LICENSE_IDENTIFIER_PREFIX
            + str(uuid.uuid4())
        )

        modules = self._normalize_capabilities(
            request.commercial_modules
        )

        entitlements = self._normalize_capabilities(
            request.feature_entitlements
        )

        deployment_identifier = request.deployment_identifier

        if (
            deployment_identifier is not None
            and not isinstance(deployment_identifier, str)
        ):
            raise LicenseIssuanceError(
                "License deployment_identifier must be a string or null."
            )

        if deployment_identifier is not None:
            deployment_identifier = (
                deployment_identifier.strip() or None
            )

        canonical_payload = {
            "organization_id": organization_id,
            "license_identifier": license_identifier,
            "commercial_edition": request.commercial_edition.value,
            "commercial_purpose": request.commercial_purpose.value,
            "license_format_version": LICENSE_FORMAT_VERSION,
            "issued_at": request.issued_at.isoformat(),
            "effective_at": request.effective_at.isoformat(),
            "expires_at": (
                request.expires_at.isoformat()
                if request.expires_at is not None
                else None
            ),
            "deployment_identifier": deployment_identifier,
            "seat_limit": request.seat_limit,
            "commercial_modules": modules,
            "feature_entitlements": entitlements,
        }

        canonical_bytes = canonicalize_license_payload(
            canonical_payload
        )

        canonical_hash = hash_canonical_license_payload(
            canonical_payload
        )

        signature = self.signing_key.private_key.sign(
            canonical_bytes,
            ec.ECDSA(
                hashes.SHA256()
            ),
        )

        return LicenseInstallRequest(
            organization_id=canonical_payload[
                "organization_id"
            ],
            license_identifier=license_identifier,
            commercial_edition=request.commercial_edition,
            commercial_purpose=request.commercial_purpose,
            license_format_version=LICENSE_FORMAT_VERSION,
            issued_at=request.issued_at,
            effective_at=request.effective_at,
            expires_at=request.expires_at,
            deployment_identifier=canonical_payload[
                "deployment_identifier"
            ],
            seat_limit=request.seat_limit,
            commercial_modules=modules,
            feature_entitlements=entitlements,
            canonical_payload=canonical_payload,
            canonical_payload_hash=canonical_hash,
            signature=base64.b64encode(
                signature
            ).decode("ascii"),
            signing_key_identifier=(
                self.signing_key.key_identifier
            ),
        )

    @staticmethod
    def _normalize_capabilities(
        values: tuple[str, ...],
    ) -> list[str]:
        if not isinstance(values, tuple):
            raise LicenseIssuanceError(
                "License capabilities must be supplied as a tuple."
            )

        normalized = []

        for value in values:
            if not isinstance(value, str):
                raise LicenseIssuanceError(
                    "License capabilities must contain only strings."
                )

            item = value.strip()

            if item and item not in normalized:
                normalized.append(item)

        return normalized
