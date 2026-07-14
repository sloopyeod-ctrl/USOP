from enum import StrEnum


class AcceptanceType(StrEnum):
    """
    Canonical duration classifications for accepted risk.

    Whether either option is allowed or requires follow-up is controlled by
    organizational governance policy.
    """

    TEMPORARY = "Temporary"
    PERMANENT = "Permanent"
