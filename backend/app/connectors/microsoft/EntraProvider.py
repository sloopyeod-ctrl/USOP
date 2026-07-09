from typing import Any

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import ConnectorConfiguration
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult


class EntraProvider(BaseConnector):
    """
    Prototype Microsoft Entra provider.

    This provider preserves the original demo connector behavior while conforming
    to the Connector Framework v2 contract.

    Future versions should replace the static demo payload with Microsoft Graph
    collection logic.
    """

    def __init__(self, configuration: ConnectorConfiguration | None = None):
        super().__init__(
            configuration
            or ConnectorConfiguration(
                provider_name="microsoft-entra",
                environment="development",
                settings={
                    "mode": "demo",
                    "source": "static",
                },
            )
        )

    def authenticate(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="authenticate",
            success=True,
            message="Demo Entra provider authentication bypassed.",
            metadata={
                "mode": self.configuration.get_setting("mode"),
                "source": self.configuration.get_setting("source"),
            },
        ).complete()

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            provider_name=self.provider_name,
            healthy=True,
            status="healthy",
            details={
                "mode": self.configuration.get_setting("mode"),
                "source": self.configuration.get_setting("source"),
            },
        )

    def collect(self) -> dict[str, Any]:
        return {
            "identities": [
                {
                    "display_name": "Marvin Dewitt",
                    "primary_email": "mgeoffdewitt@gmail.com",
                }
            ],
            "accounts": [
                {
                    "username": "mdewitt",
                    "system_name": "Microsoft Entra ID",
                }
            ],
            "groups": [
                {
                    "name": "entra-security-admins",
                }
            ],
            "roles": [
                {
                    "name": "Global Reader",
                }
            ],
            "memberships": [
                {
                    "username": "mdewitt",
                    "group_name": "entra-security-admins",
                }
            ],
            "role_assignments": [
                {
                    "username": "mdewitt",
                    "role_name": "Global Reader",
                }
            ],
        }

    def normalize(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "identities": raw_data.get("identities", []),
            "accounts": raw_data.get("accounts", []),
            "groups": raw_data.get("groups", []),
            "roles": raw_data.get("roles", []),
            "memberships": raw_data.get("memberships", []),
            "role_assignments": raw_data.get("role_assignments", []),
        }

    def synchronize(self) -> ConnectorResult:
        auth_result = self.authenticate()

        if not auth_result.success:
            return ConnectorResult(
                provider_name=self.provider_name,
                operation="synchronize",
                success=False,
                message="Authentication failed.",
                errors=auth_result.errors,
            ).complete()

        raw_data = self.collect()
        normalized_data = self.normalize(raw_data)

        records_collected = sum(len(value) for value in raw_data.values())
        records_normalized = sum(len(value) for value in normalized_data.values())

        return ConnectorResult(
            provider_name=self.provider_name,
            operation="synchronize",
            success=True,
            message="Demo Entra provider synchronized successfully.",
            records_collected=records_collected,
            records_normalized=records_normalized,
            records_synchronized=records_normalized,
            metadata={
                "mode": self.configuration.get_setting("mode"),
                "source": self.configuration.get_setting("source"),
                "objects": {
                    "identities": len(normalized_data["identities"]),
                    "accounts": len(normalized_data["accounts"]),
                    "groups": len(normalized_data["groups"]),
                    "roles": len(normalized_data["roles"]),
                    "memberships": len(normalized_data["memberships"]),
                    "role_assignments": len(normalized_data["role_assignments"]),
                },
            },
        ).complete()