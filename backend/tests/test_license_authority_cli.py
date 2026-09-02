from argparse import Namespace
from datetime import UTC, datetime

import pytest

from app.domain.commercial_edition import CommercialEdition
from app.domain.commercial_purpose import CommercialPurpose
from license_authority.cli import (
    _parse_datetime,
    build_issuance_request,
)


def _args(**overrides):
    values = {
        "organization_id": (
            "00000000-0000-0000-0000-000000000001"
        ),
        "edition": "Enterprise",
        "purpose": "Beta",
        "effective_at": "2026-09-01T12:00:00+00:00",
        "expires_at": "2026-11-30T12:00:00+00:00",
        "deployment_identifier": None,
        "seat_limit": 10,
        "commercial_modules": [
            "USOPCore",
        ],
        "feature_entitlements": [
            "IdentityDecisionPlatform",
        ],
        "signing_key_id": "unused-in-D3",
        "private_key_file": "unused-in-D3.pem",
        "output_directory": "unused-in-D3",
    }

    values.update(overrides)

    return Namespace(**values)


def test_builds_canonical_issuance_request():
    issued_at = datetime(
        2026,
        9,
        1,
        11,
        30,
        tzinfo=UTC,
    )

    request = build_issuance_request(
        _args(),
        issued_at=issued_at,
    )

    assert request.organization_id == (
        "00000000-0000-0000-0000-000000000001"
    )

    assert request.commercial_edition is (
        CommercialEdition.ENTERPRISE
    )

    assert request.commercial_purpose is (
        CommercialPurpose.BETA
    )

    assert request.issued_at == issued_at

    assert request.effective_at == datetime(
        2026,
        9,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    assert request.expires_at == datetime(
        2026,
        11,
        30,
        12,
        0,
        tzinfo=UTC,
    )

    assert request.deployment_identifier is None
    assert request.seat_limit == 10

    assert request.commercial_modules == (
        "USOPCore",
    )

    assert request.feature_entitlements == (
        "IdentityDecisionPlatform",
    )


def test_optional_expiration_remains_none():
    request = build_issuance_request(
        _args(
            expires_at=None
        ),
        issued_at=datetime(
            2026,
            9,
            1,
            tzinfo=UTC,
        ),
    )

    assert request.expires_at is None


def test_rejects_invalid_iso_timestamp():
    with pytest.raises(
        ValueError,
        match="effective_at must be a valid ISO-8601 timestamp",
    ):
        _parse_datetime(
            "not-a-timestamp",
            field_name="effective_at",
        )


def test_rejects_naive_timestamp():
    with pytest.raises(
        ValueError,
        match="effective_at must be timezone-aware",
    ):
        _parse_datetime(
            "2026-09-01T12:00:00",
            field_name="effective_at",
        )


def test_preserves_timezone_offset():
    parsed = _parse_datetime(
        "2026-09-01T08:00:00-04:00",
        field_name="effective_at",
    )

    assert parsed.utcoffset().total_seconds() == (
        -4 * 60 * 60
    )


def test_repeated_cli_capabilities_become_tuples():
    request = build_issuance_request(
        _args(
            commercial_modules=[
                "USOPCore",
                "FutureModule",
            ],
            feature_entitlements=[
                "IdentityDecisionPlatform",
                "future.feature",
            ],
        ),
        issued_at=datetime(
            2026,
            9,
            1,
            tzinfo=UTC,
        ),
    )

    assert request.commercial_modules == (
        "USOPCore",
        "FutureModule",
    )

    assert request.feature_entitlements == (
        "IdentityDecisionPlatform",
        "future.feature",
    )

def test_cli_loads_valid_signing_key_file(tmp_path):
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
    )

    from license_authority.cli import load_cli_signing_key

    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    key_path = tmp_path / "signing-key.pem"
    key_path.write_bytes(pem)

    args = _args(
        signing_key_id="test-signing-key",
        private_key_file=str(key_path),
    )

    loaded = load_cli_signing_key(args)

    assert loaded.key_identifier == (
        "test-signing-key"
    )

    assert isinstance(
        loaded.private_key.curve,
        ec.SECP256R1,
    )


def test_cli_rejects_missing_signing_key_file(tmp_path):
    from license_authority.cli import load_cli_signing_key

    args = _args(
        private_key_file=str(
            tmp_path / "missing.pem"
        )
    )

    with pytest.raises(
        ValueError,
        match="Unable to read License Authority private-key file",
    ):
        load_cli_signing_key(args)

def test_cli_issues_runtime_compatible_license_in_memory(
    tmp_path,
):
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    from app.security.license_signature_verifier import (
        LicenseSignatureVerifier,
    )
    from app.security.license_signing_keys import (
        TrustedLicenseSigningKey,
        TrustedLicenseSigningKeyRegistry,
    )
    from app.services.license_cryptographic_validator import (
        LicenseCryptographicValidator,
    )
    from license_authority.cli import (
        issue_from_cli_args,
    )

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

    args = _args(
        signing_key_id="cli-test-key",
        private_key_file=str(key_path),
    )

    issued_at = datetime(
        2026,
        9,
        1,
        11,
        30,
        tzinfo=UTC,
    )

    issued = issue_from_cli_args(
        args,
        issued_at=issued_at,
    )

    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier="cli-test-key",
                public_key_pem=public_pem,
            )
        ]
    )

    validator = LicenseCryptographicValidator(
        LicenseSignatureVerifier(
            registry
        )
    )

    result = validator.validate(
        issued
    )

    assert issued.organization_id == (
        args.organization_id
    )

    assert issued.license_identifier.startswith(
        "USOP-LIC-"
    )

    assert issued.signing_key_identifier == (
        "cli-test-key"
    )

    assert result.algorithm == (
        "ECDSA-P256-SHA256"
    )

    assert result.canonical_payload_hash == (
        issued.canonical_payload_hash
    )

def test_cli_writes_runtime_compatible_license_artifact(
    tmp_path,
):
    import json

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
    )
    from license_authority.cli import (
        issue_from_cli_args,
        write_license_artifact,
    )

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

    args = _args(
        signing_key_id="cli-artifact-test-key",
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
        output_directory=args.output_directory,
    )

    assert artifact_path.exists()

    assert artifact_path.name == (
        f"{issued.license_identifier}.license.json"
    )

    raw = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    restored = LicenseInstallRequest(
        **raw
    )

    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier="cli-artifact-test-key",
                public_key_pem=public_pem,
            )
        ]
    )

    validator = LicenseCryptographicValidator(
        LicenseSignatureVerifier(
            registry
        )
    )

    result = validator.validate(
        restored
    )

    assert restored.license_identifier == (
        issued.license_identifier
    )

    assert restored.canonical_payload == (
        issued.canonical_payload
    )

    assert restored.canonical_payload_hash == (
        issued.canonical_payload_hash
    )

    assert restored.signature == issued.signature

    assert result.algorithm == (
        "ECDSA-P256-SHA256"
    )

def test_main_issues_license_artifact(
    tmp_path,
    monkeypatch,
    capsys,
):
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
    )

    from license_authority.cli import main

    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    key_path = tmp_path / "authority.pem"
    key_path.write_bytes(private_pem)

    output_directory = tmp_path / "licenses"

    monkeypatch.setattr(
        "sys.argv",
        [
            "usop-license-authority",
            "--organization-id",
            "00000000-0000-0000-0000-000000000001",
            "--edition",
            "Enterprise",
            "--purpose",
            "Beta",
            "--effective-at",
            "2026-09-01T12:00:00+00:00",
            "--expires-at",
            "2026-11-30T12:00:00+00:00",
            "--seat-limit",
            "10",
            "--module",
            "USOPCore",
            "--entitlement",
            "IdentityDecisionPlatform",
            "--signing-key-id",
            "cli-main-test-key",
            "--private-key-file",
            str(key_path),
            "--output-directory",
            str(output_directory),
        ],
    )

    result = main()

    assert result == 0

    artifacts = list(
        output_directory.glob(
            "USOP-LIC-*.license.json"
        )
    )

    assert len(artifacts) == 1

    rendered = artifacts[0].read_text(
        encoding="utf-8"
    )

    assert "BEGIN PRIVATE KEY" not in rendered
    assert "private_key" not in rendered

    output = capsys.readouterr().out.strip()

    assert output == str(
        artifacts[0]
    )
