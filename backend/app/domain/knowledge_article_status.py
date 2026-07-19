from enum import StrEnum


class KnowledgeArticleStatus(StrEnum):
    """
    Canonical lifecycle states for reusable Organizational Knowledge.

    Knowledge evolves through controlled review and versioning.
    Historical Decision Records always reference the version that existed
    when the decision was made.
    """

    DRAFT = "Draft"
    UNDER_REVIEW = "UnderReview"
    APPROVED = "Approved"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    RETIRED = "Retired"
