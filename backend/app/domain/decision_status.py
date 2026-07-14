from enum import StrEnum


class DecisionStatus(StrEnum):
    """
    Canonical lifecycle states for a security decision record.

    Transition rules are enforced by the governance service rather than by
    this vocabulary definition.
    """

    DRAFT = "Draft"
    OPEN = "Open"
    PENDING_APPROVAL = "PendingApproval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    IN_PROGRESS = "InProgress"
    ACCEPTED = "Accepted"
    DEFERRED = "Deferred"
    ESCALATED = "Escalated"
    PENDING_VERIFICATION = "PendingVerification"
    VERIFIED = "Verified"
    CLOSED = "Closed"
    REVIEW_DUE = "ReviewDue"
    OVERDUE = "Overdue"
    REOPENED = "Reopened"
