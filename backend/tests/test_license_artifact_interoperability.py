import json

import pytest
from argparse import Namespace
from datetime import UTC, datetime

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from app.schemas.license import LicenseInstallRequest
from app.security.license_signature_verifier import (
    LicenseSignatureVerifier,
)
from app.security.license_signing_keys import (
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
)
from app.services.license_cryptographic_validator import (
    LicenseCryptographicValidator,
    LicensePayloadHashMismatchError,
    LicensePayloadSignatureError,
)
from license_authority.cli import (
    issue_from_cli_args,
    write_license_artifact,
)


KEY_IDENTIFIER = "artifact-interoperability-test-key"


def _build_artifact(tmp_path):
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    public_pem = (
        private_key
        .public_key()
        .public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo,
        )
    )

    key_path = tmp_path / "authority.pem"
    key_path.write_bytes(private_pem)

    output_directory = tmp_path / "licenses"

    args = Namespace(
        organization_id=(
            "00000000-0000-0000-0000-000000000001"
        ),
        edition="Enterprise",
        purpose="Beta",
        effective_at="2026-09-01T12:00:00+00:00",
        expires_at="2026-11-30T12:00:00+00:00",
        deployment_identifier=None,
        seat_limit=10,
        commercial_modules=[
            "USOPCore",
        ],
        feature_entitlements=[
            "IdentityDecisionPlatform",
        ],
        signing_key_id=KEY_IDENTIFIER,
        private_key_file=str(key_path),
        output_directory=str(output_directory),
    )

    issued = issue_from_cli_args(
        args,
        issued_at=datetime(
            2026,
            9,
            1,
            11,
            30,
            tzinfo=UTC,
        ),
    )

    artifact_path = write_license_artifact(
        issued,
        output_directory=str(output_directory),
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

    return artifact_path, validator


def _read_artifact(artifact_path):
    raw = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    return LicenseInstallRequest(
        **raw
    )


def test_cli_artifact_validates_after_disk_round_trip(
    tmp_path,
):
    artifact_path, validator = (
        _build_artifact(tmp_path)
    )

    restored = _read_artifact(
        artifact_path
    )

    result = validator.validate(
        restored
    )

    assert artifact_path.name == (
        f"{restored.license_identifier}.license.json"
    )

    assert result.canonical_payload_hash == (
        restored.canonical_payload_hash
    )

    assert result.signing_key_identifier == (
        KEY_IDENTIFIER
    )

    assert result.algorithm == (
        "ECDSA-P256-SHA256"
    )

def test_disk_artifact_payload_tampering_fails_closed(
    tmp_path,
):
    artifact_path, validator = (
        _build_artifact(tmp_path)
    )

    raw = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    raw["canonical_payload"][
        "seat_limit"
    ] = 9999

    tampered_path = tmp_path / "tampered-payload.license.json"

    tampered_path.write_text(
        json.dumps(
            raw,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    restored = _read_artifact(
        tampered_path
    )

    with pytest.raises(
        LicensePayloadHashMismatchError
    ):
        validator.validate(
            restored
        )


def test_disk_artifact_declared_hash_tampering_fails_closed(
    tmp_path,
):
    artifact_path, validator = (
        _build_artifact(tmp_path)
    )

    raw = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    raw["canonical_payload_hash"] = (
        "0" * 64
    )

    tampered_path = tmp_path / "tampered-hash.license.json"

    tampered_path.write_text(
        json.dumps(
            raw,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    restored = _read_artifact(
        tampered_path
    )

    with pytest.raises(
        LicensePayloadHashMismatchError
    ):
        validator.validate(
            restored
        )

def test_disk_artifact_rehashed_payload_still_fails_signature(
    tmp_path,
):
    from app.services.license_canonicalization import (
        hash_canonical_license_payload,
    )

    artifact_path, validator = (
        _build_artifact(tmp_path)
    )

    raw = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    raw["canonical_payload"][
        "seat_limit"
    ] = 9999

    raw["canonical_payload_hash"] = (
        hash_canonical_license_payload(
            raw["canonical_payload"]
        )
    )

    tampered_path = tmp_path / "rehashed-payload.license.json"

    tampered_path.write_text(
        json.dumps(
            raw,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    restored = _read_artifact(
        tampered_path
    )

    with pytest.raises(
        LicensePayloadSignatureError
    ):
        validator.validate(
            restored
        )


def test_disk_artifact_unknown_signing_key_fails_closed(
    tmp_path,
):
    artifact_path, validator = (
        _build_artifact(tmp_path)
    )

    raw = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    raw["signing_key_identifier"] = (
        "unknown-signing-key"
    )

    tampered_path = tmp_path / "unknown-key.license.json"

    tampered_path.write_text(
        json.dumps(
            raw,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    restored = _read_artifact(
        tampered_path
    )

    with pytest.raises(
        LicensePayloadSignatureError
    ):
        validator.validate(
            restored
        )

