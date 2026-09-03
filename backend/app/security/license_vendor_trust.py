from pathlib import Path

from app.security.license_signing_keys import (
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
)


USOP_LICENSE_ROOT_2026_01_IDENTIFIER = (
    "usop-license-root-2026-01"
)

_TRUSTED_KEY_DIRECTORY = (
    Path(__file__).resolve().parent
    / "trusted_license_keys"
)

USOP_LICENSE_ROOT_2026_01_PUBLIC_KEY_PEM = (
    _TRUSTED_KEY_DIRECTORY
    / "usop-license-root-2026-01.public.pem"
).read_bytes()


VENDOR_TRUSTED_LICENSE_SIGNING_KEYS: tuple[
    TrustedLicenseSigningKey,
    ...
] = (
    TrustedLicenseSigningKey(
        key_identifier=(
            USOP_LICENSE_ROOT_2026_01_IDENTIFIER
        ),
        public_key_pem=(
            USOP_LICENSE_ROOT_2026_01_PUBLIC_KEY_PEM
        ),
    ),
)


def build_vendor_license_signing_key_registry(
) -> TrustedLicenseSigningKeyRegistry:
    """
    Build the product-controlled License verification trust registry.

    Trusted public verification material is release-controlled USOP
    application material.

    Customer configuration, License artifacts, API requests, environment
    variables, and database state must not define or extend this trust root.

    The registry intentionally remains empty until the first real vendor
    public verification key is provisioned through a controlled release.
    """

    return TrustedLicenseSigningKeyRegistry(
        VENDOR_TRUSTED_LICENSE_SIGNING_KEYS
    )
