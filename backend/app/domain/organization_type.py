from enum import StrEnum


class OrganizationType(StrEnum):
    """
    Canonical operating models for a USOP Organization.

    These values describe how an organization operates USOP. They do not
    describe connected identity-provider tenants or commercial subscriptions.
    """

    CUSTOMER = "Customer"
    INTERNAL = "Internal"
    MANAGED_SERVICE_PROVIDER = "ManagedServiceProvider"
