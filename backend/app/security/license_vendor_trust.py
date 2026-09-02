from app.security.license_signing_keys import (
    TrustedLicenseSigningKey,
    TrustedLicenseSigningKeyRegistry,
)


VENDOR_TRUSTED_LICENSE_SIGNING_KEYS: tuple[
    TrustedLicenseSigningKey,
    ...
] = ()


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
