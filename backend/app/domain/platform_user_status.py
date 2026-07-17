from enum import StrEnum


class PlatformUserStatus(StrEnum):
    """
    Canonical lifecycle states for a person authorized to operate USOP.

    These values describe access lifecycle only. They do not represent
    authentication success, role resolution, Seat allocation, or License
    validity.
    """

    INVITED = "Invited"
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DISABLED = "Disabled"
