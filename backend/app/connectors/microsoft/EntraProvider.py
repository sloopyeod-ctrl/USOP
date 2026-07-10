from typing import Any

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import ConnectorConfiguration
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult
from app.security.graph.GraphClient import GraphClient


class EntraProvider(BaseConnector):
    """
    Microsoft Entra provider.

    Supports:

    - demo mode with static development data
    - live mode with Microsoft Graph user collection

    Live object types are enabled incrementally. Object types that are not yet
    implemented return empty collections to prevent demo data from being mixed
    with live tenant data.
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

    def authenticate(self) -> ConnectorResult:
        return ConnectorResult(
            provider_name=self.provider_name,
            operation="authenticate",
            success=True,
            message="Authentication handled by GraphClient.",
        ).complete()

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            provider_name=self.provider_name,
            healthy=True,
            status="healthy",
            details={
                "mode": self.configuration.get_setting("mode", "demo"),
            },
        )

    def collect(self) -> dict[str, Any]:
        mode = str(
            self.configuration.get_setting("mode", "demo")
        ).lower().strip()

        if mode == "live":
            return self.collect_live()

        if mode == "demo":
            return self.collect_demo()

        raise ValueError(
            f"Unsupported Microsoft Entra provider mode: {mode}"
        )

    def collect_live(self) -> dict[str, Any]:
        """
        Collect currently supported live Microsoft Entra resources.

        Users are live. All other resource collections remain empty until their
        individual Graph collection milestones are implemented.
        """

        return {
            "identities": self.collect_live_users(),
            "accounts": [],
            "groups": [],
            "roles": [],
            "memberships": [],
            "role_assignments": [],
        }

    def collect_live_users(self) -> list[dict[str, Any]]:
        response = self.graph.get(
            "/users",
            params={
                "$select": (
                    "id,"
                    "displayName,"
                    "userPrincipalName,"
                    "accountEnabled"
                ),
                "$top": 100,
            },
        )

        identities: list[dict[str, Any]] = []

        for user in response.get("value", []):
            display_name = user.get("displayName")
            primary_email = user.get("userPrincipalName")

            if not display_name:
                continue

            identities.append(
                {
                    "display_name": display_name,
                    "primary_email": primary_email,
                    "source_identifier": user.get("id"),
                    "status": (
                        "Active"
                        if user.get("accountEnabled", True)
                        else "Inactive"
                    ),
                }
            )

        return identities

    def collect_demo(self) -> dict[str, Any]:
        return {
            "identities": self.collect_demo_users(),
            "accounts": self.collect_demo_accounts(),
            "groups": self.collect_demo_groups(),
            "roles": self.collect_demo_roles(),
            "memberships": self.collect_demo_memberships(),
            "role_assignments": self.collect_demo_role_assignments(),
        }

    def collect_demo_users(self) -> list[dict[str, Any]]:
        return [
            {
                "display_name": "Marvin Dewitt",
                "primary_email": "mgeoffdewitt@gmail.com",
            }
        ]

    def collect_demo_accounts(self) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "system_name": "Microsoft Entra ID",
            }
        ]

    def collect_demo_groups(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "entra-security-admins",
            }
        ]

    def collect_demo_roles(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "Global Reader",
            }
        ]

    def collect_demo_memberships(self) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "group_name": "entra-security-admins",
            }
        ]

    def collect_demo_role_assignments(self) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "role_name": "Global Reader",
            }
        ]

    def normalize(
        self,
        raw_data: dict[str, Any],
    ) -> dict[str, Any]:
        return raw_data

    def synchronize(self) -> ConnectorResult:
        data = self.collect()
        records_collected = sum(
            len(value)
            for value in data.values()
            if isinstance(value, list)
        )

        return ConnectorResult(
            provider_name=self.provider_name,
            operation="synchronize",
            success=True,
            message="Microsoft Entra collection completed.",
            records_collected=records_collected,
            metadata={
                "mode": self.configuration.get_setting("mode", "demo"),
                "objects": {
                    key: len(value)
                    for key, value in data.items()
                    if isinstance(value, list)
                },
            },
        ).complete()
