from enum import StrEnum


class ApprovalStatus(StrEnum):
    """
    Canonical approval state for a decision record.

    NOT_REQUIRED is a valid policy outcome and must not be interpreted as a
    missing approval.
    """

    NOT_REQUIRED = "NotRequired"
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
