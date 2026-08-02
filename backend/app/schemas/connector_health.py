from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConnectorHealthRead(BaseModel):
    """
    Read-only operational health for one active connector provider.

    The schema represents the provider's current reported state.

    It does not represent:

    - synchronization history
    - successful remediation
    - commercial entitlement
    - customer configuration completeness
    - persistent operational history
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    provider_name: str = Field(
        min_length=1,
    )

    healthy: bool

    status: str = Field(
        min_length=1,
    )

    checked_at: datetime

    details: dict[str, Any]