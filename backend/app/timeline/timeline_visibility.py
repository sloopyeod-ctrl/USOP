from enum import StrEnum


class TimelineVisibility(StrEnum):
    """
    Canonical attention levels for operational timeline events.

    Visibility is intentionally separate from domain risk.
    """

    INFORMATION = "Information"
    NOTICE = "Notice"
    WARNING = "Warning"
    CRITICAL = "Critical"
