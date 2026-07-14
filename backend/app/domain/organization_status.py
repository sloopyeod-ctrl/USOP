from enum import StrEnum


class OrganizationStatus(StrEnum):
    """
    Canonical lifecycle states for a USOP Organization.

    Organization state is independent of subscription state. An organization
    remains historically present even when access is suspended or disabled.
    """

    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DISABLED = "Disabled"
