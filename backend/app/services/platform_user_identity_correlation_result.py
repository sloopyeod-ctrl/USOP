from dataclasses import dataclass
from enum import Enum


class PlatformUserIdentityCorrelationDisposition(str, Enum):
    DETERMINISTIC_MATCH = "DeterministicMatch"
    NO_MATCH = "NoMatch"
    AMBIGUOUS = "Ambiguous"
    UNSUPPORTED_PROVIDER = "UnsupportedProvider"
    INSUFFICIENT_EVIDENCE = "InsufficientEvidence"
    ALREADY_BOUND = "AlreadyBound"
    CONFLICT = "Conflict"


@dataclass(frozen=True)
class PlatformUserIdentityCorrelationResult:
    disposition: PlatformUserIdentityCorrelationDisposition
    organization_id: str
    platform_user_id: str
    provider_name: str | None = None
    external_tenant_id: str | None = None
    external_subject_id: str | None = None
    account_id: str | None = None
    organizational_identity_id: str | None = None
    identity_id: str | None = None
    evidence: tuple[str, ...] = ()
    message: str = ""

    @property
    def is_deterministic_match(self) -> bool:
        return self.disposition == (
            PlatformUserIdentityCorrelationDisposition.DETERMINISTIC_MATCH
        )
