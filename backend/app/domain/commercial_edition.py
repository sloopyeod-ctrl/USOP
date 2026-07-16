from enum import StrEnum


class CommercialEdition(StrEnum):
    """
    Canonical commercial packaging editions for the USOP Platform.

    Edition describes commercial packaging. It does not independently grant
    runtime capabilities; concrete modules and feature entitlements remain
    explicit parts of the signed License payload.
    """

    COMMUNITY = "Community"
    STARTER = "Starter"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"
