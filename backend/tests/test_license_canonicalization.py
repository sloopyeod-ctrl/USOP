import hashlib

import pytest

from app.services.license_canonicalization import (
    LicenseCanonicalizationError,
    canonicalize_license_payload,
    hash_canonical_license_payload,
)


def test_canonicalization_is_deterministic_across_key_order():
    first = {
        "organization_id": "org-1",
        "commercial_edition": "Enterprise",
        "seat_limit": 25,
    }

    second = {
        "seat_limit": 25,
        "commercial_edition": "Enterprise",
        "organization_id": "org-1",
    }

    assert canonicalize_license_payload(first) == (
        canonicalize_license_payload(second)
    )


def test_canonicalization_removes_insignificant_whitespace():
    payload = {
        "b": 2,
        "a": 1,
    }

    assert canonicalize_license_payload(payload) == b'{"a":1,"b":2}'


def test_canonicalization_preserves_unicode_as_utf8():
    payload = {
        "customer_name": "Café Security",
    }

    canonical = canonicalize_license_payload(payload)

    assert canonical == '{"customer_name":"Café Security"}'.encode(
        "utf-8"
    )


def test_hash_matches_sha256_of_canonical_bytes():
    payload = {
        "organization_id": "org-1",
        "feature_entitlements": [
            "identity.core",
            "governance.decisions",
        ],
    }

    canonical = canonicalize_license_payload(payload)

    assert hash_canonical_license_payload(payload) == (
        hashlib.sha256(canonical).hexdigest()
    )


def test_nested_objects_are_deterministic():
    first = {
        "features": {
            "b": False,
            "a": True,
        },
    }

    second = {
        "features": {
            "a": True,
            "b": False,
        },
    }

    assert canonicalize_license_payload(first) == (
        canonicalize_license_payload(second)
    )


def test_array_order_is_preserved():
    first = {
        "modules": [
            "identity",
            "governance",
        ],
    }

    second = {
        "modules": [
            "governance",
            "identity",
        ],
    }

    assert canonicalize_license_payload(first) != (
        canonicalize_license_payload(second)
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": float("-inf")},
    ],
)
def test_non_json_numeric_values_fail_closed(payload):
    with pytest.raises(
        LicenseCanonicalizationError,
    ):
        canonicalize_license_payload(payload)


def test_non_dictionary_payload_fails_closed():
    with pytest.raises(
        LicenseCanonicalizationError,
    ):
        canonicalize_license_payload(["not", "an", "object"])


def test_unsupported_python_type_fails_closed():
    with pytest.raises(
        LicenseCanonicalizationError,
    ):
        canonicalize_license_payload(
            {
                "unsupported": object(),
            }
        )


def test_known_canonicalization_vector_is_stable():
    payload = {
        "commercial_edition": "Enterprise",
        "organization_id": (
            "00000000-0000-0000-0000-000000000001"
        ),
        "seat_limit": 25,
    }

    expected_canonical = (
        b'{"commercial_edition":"Enterprise",'
        b'"organization_id":'
        b'"00000000-0000-0000-0000-000000000001",'
        b'"seat_limit":25}'
    )

    expected_hash = (
        "e329d9b9bdabeeaa5a2c13a0827bc8f8"
        "6c7a6b3c452a022cb63f218d8a9d73a2"
    )

    assert canonicalize_license_payload(payload) == (
        expected_canonical
    )

    assert hash_canonical_license_payload(payload) == (
        expected_hash
    )
