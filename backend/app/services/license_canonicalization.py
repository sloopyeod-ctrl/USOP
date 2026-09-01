import hashlib
import json
from typing import Any


class LicenseCanonicalizationError(ValueError):
    """Raised when a License payload cannot be canonically serialized."""


def canonicalize_license_payload(
    payload: dict[str, Any],
) -> bytes:
    """
    Serialize a License payload into deterministic UTF-8 JSON bytes.

    Canonicalization contract:

    - input must be a dictionary;
    - object keys are sorted;
    - insignificant whitespace is removed;
    - Unicode is preserved rather than ASCII-escaped;
    - NaN and Infinity are rejected;
    - output is UTF-8 bytes.

    These bytes are the authoritative input for License hashing and
    cryptographic signing.
    """

    if not isinstance(payload, dict):
        raise LicenseCanonicalizationError(
            "License canonical payload must be a JSON object."
        )

    try:
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise LicenseCanonicalizationError(
            "License payload contains unsupported canonical JSON data."
        ) from error

    return serialized.encode("utf-8")


def hash_canonical_license_payload(
    payload: dict[str, Any],
) -> str:
    """
    Return the lowercase SHA-256 digest of canonical License payload bytes.
    """

    canonical = canonicalize_license_payload(payload)

    return hashlib.sha256(canonical).hexdigest()
