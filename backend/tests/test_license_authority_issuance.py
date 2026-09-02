from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from app.security.license_signature_verifier import (
    LicenseSignatureVerifier,
)
from app.security.license_signing_keys import (
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
)
from app.services.license_cryptographic_validator import (
    LicenseCryptographicValidator,
    LicensePayloadSignatureError,
)
from app.services.license_canonicalization import (
    hash_canonical_license_payload,
)

from license_authority.issuance import (
    LICENSE_FORMAT_VERSION,
    LicenseIssuanceError,
    LicenseIssuanceRequest,
    LicenseIssuanceService,
)
from license_authority.signing_key import (
    load_license_authority_signing_key,
)


KEY_IDENTIFIER = "usop-test-authority-2026-01"
ORGANIZATION_ID = "00000000-0000-0000-0000-000000000001"


def _build_authority_and_validator():
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    authority_key = load_license_authority_signing_key(
        key_identifier=KEY_IDENTIFIER,
        private_key_pem=private_pem,
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

    validator = LicenseCryptographicValidator(
        LicenseSignatureVerifier(
            registry
        )
    )

    return authority_key, validator


def _issuance_request():
    issued_at = datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )

    return LicenseIssuanceRequest(
        organization_id=ORGANIZATION_ID,
        commercial_edition=CommercialEdition.ENTERPRISE,
        commercial_purpose=CommercialPurpose.BETA,
        issued_at=issued_at,
        effective_at=issued_at,
        expires_at=issued_at + timedelta(days=90),
        deployment_identifier=None,
        seat_limit=10,
        commercial_modules=(
            "USOPCore",
        ),
        feature_entitlements=(
            "IdentityDecisionPlatform",
        ),
    )


def test_issuer_creates_runtime_compatible_signed_license():
    authority_key, validator = (
        _build_authority_and_validator()
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        _issuance_request()
    )

    result = validator.validate(
        issued
    )

    assert issued.license_identifier.startswith(
        "USOP-LIC-"
    )

    assert issued.license_format_version == (
        LICENSE_FORMAT_VERSION
    )

    assert result.canonical_payload_hash == (
        issued.canonical_payload_hash
    )

    assert result.signing_key_identifier == (
        KEY_IDENTIFIER
    )

    assert result.algorithm == (
        "ECDSA-P256-SHA256"
    )


def test_all_commercial_envelope_fields_are_signed():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        _issuance_request()
    )

    payload = issued.canonical_payload

    assert payload == {
        "organization_id": issued.organization_id,
        "license_identifier": issued.license_identifier,
        "commercial_edition": issued.commercial_edition.value,
        "commercial_purpose": issued.commercial_purpose.value,
        "license_format_version": issued.license_format_version,
        "issued_at": issued.issued_at.isoformat(),
        "effective_at": issued.effective_at.isoformat(),
        "expires_at": issued.expires_at.isoformat(),
        "deployment_identifier": issued.deployment_identifier,
        "seat_limit": issued.seat_limit,
        "commercial_modules": issued.commercial_modules,
        "feature_entitlements": issued.feature_entitlements,
    }


def test_payload_hash_matches_complete_signed_payload():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        _issuance_request()
    )

    assert issued.canonical_payload_hash == (
        hash_canonical_license_payload(
            issued.canonical_payload
        )
    )


@pytest.mark.parametrize(
    (
        "field",
        "replacement",
    ),
    [
        ("expires_at", "2099-01-01T00:00:00+00:00"),
        ("deployment_identifier", "forged-deployment"),
        ("seat_limit", 9999),
        ("commercial_modules", ["ForgedModule"]),
        ("feature_entitlements", ["forged.entitlement"]),
    ],
)
def test_mutating_signed_commercial_field_fails_verification(
    field,
    replacement,
):
    authority_key, validator = (
        _build_authority_and_validator()
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        _issuance_request()
    )

    tampered_payload = dict(
        issued.canonical_payload
    )

    tampered_payload[field] = replacement

    tampered = issued.model_copy(
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
        LicensePayloadSignatureError
    ):
        validator.validate(
            tampered
        )


def test_normalizes_capability_lists_before_signing():
    authority_key, validator = (
        _build_authority_and_validator()
    )

    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=(
            " USOPCore ",
            "USOPCore",
            "",
        ),
        feature_entitlements=(
            " IdentityDecisionPlatform ",
            "IdentityDecisionPlatform",
            "",
        ),
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        request
    )

    assert issued.commercial_modules == [
        "USOPCore"
    ]

    assert issued.feature_entitlements == [
        "IdentityDecisionPlatform"
    ]

    validator.validate(
        issued
    )


def test_each_issuance_receives_unique_identifier():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    service = LicenseIssuanceService(
        authority_key
    )

    first = service.issue(
        _issuance_request()
    )

    second = service.issue(
        _issuance_request()
    )

    assert first.license_identifier != (
        second.license_identifier
    )

    assert first.license_identifier.startswith(
        "USOP-LIC-"
    )

    assert second.license_identifier.startswith(
        "USOP-LIC-"
    )


def test_issuer_does_not_expose_private_key_in_license():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    issued = LicenseIssuanceService(
        authority_key
    ).issue(
        _issuance_request()
    )

    serialized = issued.model_dump_json()

    assert "BEGIN PRIVATE KEY" not in serialized
    assert "private_key" not in serialized

def test_rejects_empty_organization_id():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id="   ",
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(
        LicenseIssuanceError
    ):
        LicenseIssuanceService(
            authority_key
        ).issue(
            request
        )


def test_rejects_invalid_seat_limit():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=0,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(
        LicenseIssuanceError
    ):
        LicenseIssuanceService(
            authority_key
        ).issue(
            request
        )


def test_rejects_expiration_not_after_effective_date():
    authority_key, _ = (
        _build_authority_and_validator()
    )

    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.effective_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(
        LicenseIssuanceError
    ):
        LicenseIssuanceService(
            authority_key
        ).issue(
            request
        )

def test_rejects_non_string_deployment_identifier():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=123,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)


def test_rejects_non_tuple_capability_collection():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=["USOPCore"],
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)


def test_rejects_non_string_capability_value():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=(
            "USOPCore",
            123,
        ),
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)

def test_rejects_noncanonical_commercial_edition():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition="Enterprise",
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)


def test_rejects_noncanonical_commercial_purpose():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose="Beta",
        issued_at=request.issued_at,
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)


def test_rejects_non_datetime_issued_at():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at="2026-09-01T12:00:00+00:00",
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)


def test_rejects_naive_datetime():
    authority_key, _ = _build_authority_and_validator()
    request = _issuance_request()

    request = LicenseIssuanceRequest(
        organization_id=request.organization_id,
        commercial_edition=request.commercial_edition,
        commercial_purpose=request.commercial_purpose,
        issued_at=request.issued_at.replace(
            tzinfo=None
        ),
        effective_at=request.effective_at,
        expires_at=request.expires_at,
        deployment_identifier=request.deployment_identifier,
        seat_limit=request.seat_limit,
        commercial_modules=request.commercial_modules,
        feature_entitlements=request.feature_entitlements,
    )

    with pytest.raises(LicenseIssuanceError):
        LicenseIssuanceService(
            authority_key
        ).issue(request)
