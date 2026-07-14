from enum import StrEnum


class VerificationStatus(StrEnum):
    """
    Canonical verification state for corrective or compensating actions.

    Verification requirements remain organization-configurable.
    """

    NOT_REQUIRED = "NotRequired"
    PENDING = "Pending"
    VERIFIED = "Verified"
    FAILED = "Failed"
