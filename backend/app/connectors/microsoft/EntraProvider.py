from typing import Any

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import (
    ConnectorConfiguration,
)
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult
from app.security.graph.GraphClient import GraphClient


class EntraProvider(BaseConnector):
    """
    Microsoft Entra connector provider.

    The provider translates Microsoft Graph resources into provider-neutral
    USOP collection records.

    Supported modes:

    - demo:
        Returns static development records.

    - live:
        Collects supported resources from Microsoft Graph.

    Live capabilities are enabled incrementally. Unsupported live collections
    return empty lists so demo records are never mixed with live tenant data.

    Current live capabilities:

    - identities derived from Microsoft Entra users
    - accounts derived from Microsoft Entra users
    """

    PROVIDER_NAME = "microsoft-entra"
    SYSTEM_NAME = "Microsoft Entra ID"

    def __init__(
        self,
        configuration: ConnectorConfiguration | None = None,
        graph_client: GraphClient | None = None,
    ):
        super().__init__(
            configuration
            or ConnectorConfiguration(
                provider_name=self.PROVIDER_NAME,
                environment="development",
                settings={
                    "mode": "live",
                },
            )
        )

        self.graph = graph_client or GraphClient()

    def authenticate(self) -> ConnectorResult:
        """
        Report connector authentication readiness.

        GraphClient owns token acquisition and authenticated request handling.
        """

        return ConnectorResult(
            provider_name=self.provider_name,
            operation="authenticate",
            success=True,
            message="Authentication handled by GraphClient.",
        ).complete()

    def health(self) -> ConnectorHealth:
        """
        Return the configured operating state of the provider.
        """

        return ConnectorHealth(
            provider_name=self.provider_name,
            healthy=True,
            status="healthy",
            details={
                "mode": self.configuration.get_setting(
                    "mode",
                    "demo",
                ),
                "live_capabilities": [
                    "identities",
                    "accounts",
                ],
            },
        )

    def collect(self) -> dict[str, Any]:
        """
        Collect resources for the configured provider mode.
        """

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

        A Microsoft Entra user represents two distinct USOP concepts:

        - an identity representing the security principal
        - an account representing the principal in Microsoft Entra

        Both collections are created from one Microsoft Graph request so the
        connector does not perform duplicate collection work.

        Collections not yet supported remain empty until their individual
        milestones are implemented.
        """

        graph_users = self._collect_live_user_records()

        return {
            "identities": self._build_live_identities(graph_users),
            "accounts": self._build_live_accounts(graph_users),
            "groups": [],
            "roles": [],
            "memberships": [],
            "role_assignments": [],
        }

    def _collect_live_user_records(self) -> list[dict[str, Any]]:
        """
        Retrieve the Microsoft Graph user records needed by the currently
        supported identity and account translations.

        Pagination will be introduced as a separate connector capability.
        """

        response = self.graph.get(
            "/users",
            params={
                "$select": (
                    "id,"
                    "displayName,"
                    "userPrincipalName,"
                    "accountEnabled,"
                    "userType"
                ),
                "$top": 100,
            },
        )

        records = response.get("value", [])

        if not isinstance(records, list):
            raise ValueError(
                "Microsoft Graph users response did not contain a valid "
                "'value' collection."
            )

        return [
            record
            for record in records
            if isinstance(record, dict)
        ]

    def _build_live_identities(
        self,
        graph_users: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Translate Microsoft Graph users into canonical identity records.
        """

        identities: list[dict[str, Any]] = []

        for user in graph_users:
            source_identifier = self._clean_string(user.get("id"))
            display_name = self._clean_string(
                user.get("displayName")
            )
            primary_email = self._clean_string(
                user.get("userPrincipalName")
            )

            if not source_identifier or not display_name:
                continue

            identities.append(
                {
                    "display_name": display_name,
                    "identity_class": "Person",
                    "primary_email": primary_email,
                    "status": self._status_from_account_enabled(
                        user.get("accountEnabled")
                    ),
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": source_identifier,
                    "confidence_score": 100,
                }
            )

        return identities

    def _build_live_accounts(
        self,
        graph_users: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Translate Microsoft Graph users into provider account records.

        identity_source_system and identity_source_identifier provide a
        provider-neutral correlation reference. Persistence support for this
        reference will be introduced in the next milestone.
        """

        accounts: list[dict[str, Any]] = []

        for user in graph_users:
            source_identifier = self._clean_string(user.get("id"))
            username = self._clean_string(
                user.get("userPrincipalName")
            )
            display_name = self._clean_string(
                user.get("displayName")
            )

            if not source_identifier or not username:
                continue

            accounts.append(
                {
                    "username": username,
                    "display_name": display_name,
                    "account_type": self._account_type_from_user_type(
                        user.get("userType")
                    ),
                    "status": self._status_from_account_enabled(
                        user.get("accountEnabled")
                    ),
                    "system_name": self.SYSTEM_NAME,
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": source_identifier,
                    "identity_source_system": self.SYSTEM_NAME,
                    "identity_source_identifier": source_identifier,
                    "confidence_score": 100,
                }
            )

        return accounts

    def collect_live_users(self) -> list[dict[str, Any]]:
        """
        Collect live identities derived from Microsoft Entra users.

        This public method remains available for compatibility with existing
        development tools. collect_live() should be preferred when multiple
        supported collections are needed from one Graph request.
        """

        graph_users = self._collect_live_user_records()
        return self._build_live_identities(graph_users)

    def collect_live_accounts(self) -> list[dict[str, Any]]:
        """
        Collect live accounts derived from Microsoft Entra users.

        collect_live() should be preferred when identities and accounts are
        needed together because it avoids a duplicate Graph request.
        """

        graph_users = self._collect_live_user_records()
        return self._build_live_accounts(graph_users)

    def collect_demo(self) -> dict[str, Any]:
        """
        Return provider-neutral static development records.
        """

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
                "identity_class": "Person",
                "primary_email": "mgeoffdewitt@gmail.com",
                "status": "Active",
                "source_system": self.SYSTEM_NAME,
                "source_identifier": "demo-user-marvin-dewitt",
                "confidence_score": 100,
            }
        ]

    def collect_demo_accounts(self) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "display_name": "Marvin Dewitt",
                "account_type": "User",
                "status": "Active",
                "system_name": self.SYSTEM_NAME,
                "source_system": self.SYSTEM_NAME,
                "source_identifier": "demo-account-mdewitt",
                "identity_source_system": self.SYSTEM_NAME,
                "identity_source_identifier": (
                    "demo-user-marvin-dewitt"
                ),
                "confidence_score": 100,
            }
        ]

    def collect_demo_groups(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "entra-security-admins",
                "display_name": "Entra Security Administrators",
                "group_type": "Security",
                "status": "Active",
                "system_name": self.SYSTEM_NAME,
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-group-entra-security-admins"
                ),
                "confidence_score": 100,
            }
        ]

    def collect_demo_roles(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "Global Reader",
                "display_name": "Global Reader",
                "role_type": "Directory",
                "status": "Active",
                "system_name": self.SYSTEM_NAME,
                "source_system": self.SYSTEM_NAME,
                "source_identifier": "demo-role-global-reader",
                "confidence_score": 100,
            }
        ]

    def collect_demo_memberships(self) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "group_name": "entra-security-admins",
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-membership-mdewitt-security-admins"
                ),
            }
        ]

    def collect_demo_role_assignments(self) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "role_name": "Global Reader",
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-role-assignment-mdewitt-global-reader"
                ),
            }
        ]

    def normalize(
        self,
        raw_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Return collected provider records.

        Canonical normalization remains the responsibility of the shared
        NormalizationEngine.
        """

        return raw_data

    def synchronize(self) -> ConnectorResult:
        """
        Execute provider collection and return connector-level metrics.
        """

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
                "mode": self.configuration.get_setting(
                    "mode",
                    "demo",
                ),
                "objects": {
                    key: len(value)
                    for key, value in data.items()
                    if isinstance(value, list)
                },
            },
        ).complete()

    @staticmethod
    def _clean_string(value: Any) -> str | None:
        """
        Convert a provider value into a trimmed string.
        """

        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _status_from_account_enabled(
        account_enabled: Any,
    ) -> str:
        """
        Translate the provider account state into a canonical status.
        """

        if account_enabled is False:
            return "Inactive"

        return "Active"

    @staticmethod
    def _account_type_from_user_type(
        user_type: Any,
    ) -> str:
        """
        Translate the Entra userType value into a canonical account type.

        Entra Member users are represented as User accounts. Entra Guest
        users are represented as External accounts.
        """

        normalized_user_type = str(user_type or "").strip().lower()

        if normalized_user_type == "guest":
            return "External"

        return "User"
