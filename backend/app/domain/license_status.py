from enum import StrEnum


class LicenseStatus(StrEnum):
    """
    Canonical lifecycle classification for an issued USOP License.

    License status describes the commercial record itself. Runtime conditions
    such as expiration, grace periods, validation failures, and effective
    entitlement belong to derived Subscription State and must not be persisted
    here as mutable License lifecycle state.
    """

    ISSUED = "Issued"
    SUPERSEDED = "Superseded"
    REVOKED = "Revoked"
