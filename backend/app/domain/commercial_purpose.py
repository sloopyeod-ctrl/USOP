from enum import StrEnum


class CommercialPurpose(StrEnum):
    """
    Canonical purpose for which an immutable USOP License was issued.

    Purpose remains separate from Commercial Edition so evaluation, beta,
    internal, partner, and production licenses can use the same platform
    packaging without introducing special-case runtime logic.
    """

    INTERNAL = "Internal"
    DEVELOPMENT = "Development"
    EVALUATION = "Evaluation"
    BETA = "Beta"
    PRODUCTION = "Production"
    PARTNER = "Partner"
