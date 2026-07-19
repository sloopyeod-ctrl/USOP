from enum import StrEnum


class KnowledgeAssetStatus(StrEnum):
    """
    Canonical lifecycle states for reusable Organizational Memory assets.

    Knowledge Assets evolve through controlled review and lifecycle
    governance while retaining a stable organizational identity.
    """

    DRAFT = "Draft"
    UNDER_REVIEW = "UnderReview"
    APPROVED = "Approved"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    RETIRED = "Retired"
