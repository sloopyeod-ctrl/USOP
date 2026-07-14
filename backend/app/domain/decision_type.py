from enum import StrEnum


class DecisionType(StrEnum):
    """
    Canonical organizational responses to a security decision opportunity.

    These values describe what the organization chose to do. They do not
    define approval, review, or verification requirements; those remain
    configurable through governance policy.
    """

    ACCEPT_RISK = "AcceptRisk"
    CORRECT_RISK = "CorrectRisk"
    ESCALATE = "Escalate"
    DEFER = "Defer"
    FALSE_POSITIVE = "FalsePositive"
