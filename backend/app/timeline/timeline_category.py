from enum import StrEnum


class TimelineCategory(StrEnum):
    """
    Canonical operational domains represented by the USOP timeline.

    Categories describe operational meaning, not database entities.
    """

    OPERATIONAL = "Operational"
    AUTHORIZATION = "Authorization"
    IDENTITY = "Identity"
    DECISION = "Decision"
    KNOWLEDGE = "Knowledge"
    GOVERNANCE = "Governance"
    THREAT = "Threat"
    CLOUD = "Cloud"
    COMPLIANCE = "Compliance"
    ASSET = "Asset"
    SYSTEM = "System"
