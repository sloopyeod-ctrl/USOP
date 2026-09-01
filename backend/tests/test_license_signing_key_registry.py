import pytest

from app.security.license_signing_keys import (
    DuplicateLicenseSigningKeyError,
    InvalidLicenseSigningKeyError,
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
    UnknownLicenseSigningKeyError,
)


PUBLIC_KEY_ONE = b"""-----BEGIN PUBLIC KEY-----
TEST-PUBLIC-KEY-ONE
-----END PUBLIC KEY-----
"""

PUBLIC_KEY_TWO = b"""-----BEGIN PUBLIC KEY-----
TEST-PUBLIC-KEY-TWO
-----END PUBLIC KEY-----
"""


def test_registry_resolves_known_signing_key():
    expected = TrustedLicenseSigningKey(
        key_identifier="usop-license-root-2026-01",
        public_key_pem=PUBLIC_KEY_ONE,
    )

    registry = TrustedLicenseSigningKeyRegistry(
        [expected]
    )

    assert registry.resolve(
        "usop-license-root-2026-01"
    ) == expected


def test_key_identifier_is_normalized():
    key = TrustedLicenseSigningKey(
        key_identifier="  usop-license-root-2026-01  ",
        public_key_pem=PUBLIC_KEY_ONE,
    )

    assert key.key_identifier == (
        "usop-license-root-2026-01"
    )


def test_registry_resolve_normalizes_identifier():
    expected = TrustedLicenseSigningKey(
        key_identifier="usop-license-root-2026-01",
        public_key_pem=PUBLIC_KEY_ONE,
    )

    registry = TrustedLicenseSigningKeyRegistry(
        [expected]
    )

    assert registry.resolve(
        "  usop-license-root-2026-01  "
    ) == expected


def test_unknown_signing_key_fails_closed():
    registry = TrustedLicenseSigningKeyRegistry()

    with pytest.raises(
        UnknownLicenseSigningKeyError,
    ):
        registry.resolve(
            "unknown-license-key"
        )


def test_empty_identifier_fails_closed():
    registry = TrustedLicenseSigningKeyRegistry()

    with pytest.raises(
        UnknownLicenseSigningKeyError,
    ):
        registry.resolve("   ")


def test_duplicate_signing_key_identifier_is_rejected():
    first = TrustedLicenseSigningKey(
        key_identifier="usop-license-root-2026-01",
        public_key_pem=PUBLIC_KEY_ONE,
    )

    second = TrustedLicenseSigningKey(
        key_identifier="usop-license-root-2026-01",
        public_key_pem=PUBLIC_KEY_TWO,
    )

    with pytest.raises(
        DuplicateLicenseSigningKeyError,
    ):
        TrustedLicenseSigningKeyRegistry(
            [
                first,
                second,
            ]
        )


def test_empty_trusted_key_identifier_is_rejected():
    with pytest.raises(
        InvalidLicenseSigningKeyError,
    ):
        TrustedLicenseSigningKey(
            key_identifier="   ",
            public_key_pem=PUBLIC_KEY_ONE,
        )


def test_empty_public_key_material_is_rejected():
    with pytest.raises(
        InvalidLicenseSigningKeyError,
    ):
        TrustedLicenseSigningKey(
            key_identifier="usop-license-root-2026-01",
            public_key_pem=b"",
        )


def test_non_bytes_public_key_material_is_rejected():
    with pytest.raises(
        InvalidLicenseSigningKeyError,
    ):
        TrustedLicenseSigningKey(
            key_identifier="usop-license-root-2026-01",
            public_key_pem="not-bytes",  # type: ignore[arg-type]
        )


def test_registry_reports_known_and_unknown_keys():
    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier="usop-license-root-2026-01",
                public_key_pem=PUBLIC_KEY_ONE,
            )
        ]
    )

    assert registry.contains(
        "usop-license-root-2026-01"
    )
    assert not registry.contains(
        "untrusted-key"
    )


def test_registry_identifiers_are_deterministic():
    registry = TrustedLicenseSigningKeyRegistry(
        [
            TrustedLicenseSigningKey(
                key_identifier="key-b",
                public_key_pem=PUBLIC_KEY_TWO,
            ),
            TrustedLicenseSigningKey(
                key_identifier="key-a",
                public_key_pem=PUBLIC_KEY_ONE,
            ),
        ]
    )

    assert registry.identifiers() == (
        "key-a",
        "key-b",
    )


def test_registry_exposes_no_private_key_attribute():
    key = TrustedLicenseSigningKey(
        key_identifier="usop-license-root-2026-01",
        public_key_pem=PUBLIC_KEY_ONE,
    )

    assert not hasattr(
        key,
        "private_key",
    )
    assert not hasattr(
        key,
        "private_key_pem",
    )
