from enum import StrEnum


class AuthorizationRiskLevel(StrEnum):
    """
    Canonical authorization-risk levels used by USOP.

    UNKNOWN is intentional. USOP must preserve uncertainty rather than
    inventing a security classification when evidence is incomplete.
    """

    CRITICAL = "Critical"
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"
    UNKNOWN = "Unknown"
