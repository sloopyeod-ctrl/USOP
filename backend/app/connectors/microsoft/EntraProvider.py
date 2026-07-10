from typing import Any

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import ConnectorConfiguration
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult
from app.security.graph.GraphClient import GraphClient


class EntraProvider(BaseConnector):
    """
    Microsoft Entra Provider.

    Supports both:

    - demo mode
    - live Microsoft Graph mode

    Additional Microsoft Graph object collection will be added incrementally.
    """

    def __init__(self, configuration: ConnectorConfiguration | None = None):
        super().__init__(
            configuration
            or ConnectorConfiguration(
                provider_name="microsoft-entra",
                environment="development",
                settings={
                    "mode": "live",
                },
            )
        )

        self.graph = GraphClient()

    #
    # Authentication
    #

    def authenticate(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="authenticate",
            success=True,
            message="Authentication handled by GraphClient.",
        ).complete()

    #
    # Health
    #

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            provider_name=self.provider_name,
            healthy=True,
            status="healthy",
        )

    #
    # Public Collection
    #

    def collect(self) -> dict[str, Any]:
        mode = self.configuration.get_setting("mode", "demo").lower()

        if mode == "live":
            identities = self.collect_live_users()
        else:
            identities = self.collect_demo_users()

        return {
            "identities": identities,
            "accounts": self.collect_demo_accounts(),
            "groups": self.collect_demo_groups(),
            "roles": self.collect_demo_roles(),
            "memberships": self.collect_demo_memberships(),
            "role_assignments": self.collect_demo_role_assignments(),
        }

    #
    # Live Microsoft Graph
    #

    def collect_live_users(self) -> list[dict[str, Any]]:
        response = self.graph.get(
            "/users",
            params={
                "$select": "displayName,userPrincipalName",
                "$top": 100,
            },
        )

        identities = []

        for user in response.get("value", []):
            identities.append(
                {
                    "display_name": user.get("displayName"),
                    "primary_email": user.get("userPrincipalName"),
                }
            )

        return identities

    #
    # Demo Data
    #

    def collect_demo_users(self):
        return [
            {
                "display_name": "Marvin Dewitt",
                "primary_email": "mgeoffdewitt@gmail.com",
            }
        ]

    def collect_demo_accounts(self):
        return [
            {
                "username": "mdewitt",
                "system_name": "Microsoft Entra ID",
            }
        ]

    def collect_demo_groups(self):
        return [
            {
                "name": "entra-security-admins",
            }
        ]

    def collect_demo_roles(self):
        return [
            {
                "name": "Global Reader",
            }
        ]

    def collect_demo_memberships(self):
        return [
            {
                "username": "mdewitt",
                "group_name": "entra-security-admins",
            }
        ]

    def collect_demo_role_assignments(self):
        return [
            {
                "username": "mdewitt",
                "role_name": "Global Reader",
            }
        ]

    #
    # Normalization
    #

    def normalize(self, raw_data):
        return raw_data

    #
    # Synchronization
    #

    def synchronize(self):
        data = self.collect()

        return ConnectorResult(
            provider_name=self.provider_name,
            operation="synchronize",
            success=True,
            message="Collection completed.",
            records_collected=sum(len(v) for v in data.values()),
        ).complete()