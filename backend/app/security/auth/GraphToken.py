from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class GraphToken:
    access_token: str
    token_type: str
    expires_at: datetime

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    def authorization_header(self) -> dict[str, str]:
        return {
            "Authorization": f"{self.token_type} {self.access_token}",
        }