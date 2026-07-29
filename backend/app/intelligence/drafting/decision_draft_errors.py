class DecisionDraftIntelligenceError(
    ValueError
):
    """
    Base error for decision-draft intelligence operations.
    """


class DecisionDraftIntelligenceValidationError(
    DecisionDraftIntelligenceError
):
    """
    Raised when required draft scoping information is invalid.
    """


class DecisionDraftIdentityNotFoundError(
    DecisionDraftIntelligenceError
):
    """
    Raised when identity intelligence cannot be resolved.
    """


class DecisionDraftRecommendationNotFoundError(
    DecisionDraftIntelligenceError
):
    """
    Raised when the requested recommendation is unavailable.
    """
