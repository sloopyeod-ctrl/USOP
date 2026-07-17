from enum import StrEnum


class PlatformRoleStatus(StrEnum):
    """
    Canonical lifecycle states for a USOP Platform Role.

    Role lifecycle is separate from Platform User lifecycle, authentication,
    License validity, Seat allocation, and permission resolution.
    """

    ACTIVE = "Active"
    DISABLED = "Disabled"
