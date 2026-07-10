from typing import Any

from app.connectors.core.BaseConnector import BaseConnector
from app.connectors.core.ConnectorConfiguration import (
    ConnectorConfiguration,
)
from app.connectors.core.ConnectorHealth import ConnectorHealth
from app.connectors.core.ConnectorResult import ConnectorResult
from app.domain.principal_type import PrincipalType
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
    - groups derived from Microsoft Entra groups
    - direct group memberships derived from Microsoft Entra group members
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
                    "groups",
                    "memberships",
                ],
            },
        )

    def collect(self) -> dict[str, Any]:
        """
        Collect resources for the configured provider mode.
        """

        mode = str(
            self.configuration.get_setting(
                "mode",
                "demo",
            )
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

        Microsoft Entra users are translated into both canonical identities
        and provider accounts from one Graph request.

        Microsoft Entra groups are collected independently and reused for
        direct membership collection.

        Membership records contain provider source references rather than
        PostgreSQL identifiers. Canonical database identifiers are resolved
        later by reconciliation.

        Collections not yet supported remain empty until their individual
        milestones are implemented.
        """

        graph_users = self._collect_live_user_records()
        graph_groups = self._collect_live_group_records()

        return {
            "identities": self._build_live_identities(
                graph_users
            ),
            "accounts": self._build_live_accounts(
                graph_users
            ),
            "groups": self._build_live_groups(
                graph_groups
            ),
            "roles": [],
            "memberships": (
                self._collect_and_build_live_memberships(
                    graph_groups
                )
            ),
            "role_assignments": [],
        }

    def _collect_live_user_records(
        self,
    ) -> list[dict[str, Any]]:
        """
        Retrieve Microsoft Graph user records needed by supported identity
        and account translations.

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

        return self._extract_graph_collection(
            response=response,
            resource_name="users",
        )

    def _collect_live_group_records(
        self,
    ) -> list[dict[str, Any]]:
        """
        Retrieve Microsoft Graph group records needed by group and membership
        translations.

        Provider-native properties are used only inside the connector.

        Pagination will be introduced as a separate connector capability.
        """

        response = self.graph.get(
            "/groups",
            params={
                "$select": (
                    "id,"
                    "displayName,"
                    "description,"
                    "securityEnabled,"
                    "mailEnabled,"
                    "groupTypes,"
                    "membershipRule,"
                    "membershipRuleProcessingState"
                ),
                "$top": 100,
            },
        )

        return self._extract_graph_collection(
            response=response,
            resource_name="groups",
        )

    def _collect_live_group_member_records(
        self,
        group: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Retrieve direct Microsoft Entra members for one group.

        The returned records retain the Graph object type so the connector can
        translate users, service principals, devices, nested groups, and other
        supported principals into the canonical PrincipalType vocabulary.

        Transitive membership is intentionally not collected in this
        milestone.
        """

        group_identifier = self._clean_string(
            group.get("id")
        )
        group_name = self._clean_string(
            group.get("displayName")
        )

        if not group_identifier:
            return []

        response = self.graph.get(
            f"/groups/{group_identifier}/members",
            params={
                "$select": (
                    "id,"
                    "displayName,"
                    "userPrincipalName,"
                    "appId,"
                    "deviceId"
                ),
                "$top": 100,
            },
        )

        resource_name = (
            f"group members for {group_name or group_identifier}"
        )

        return self._extract_graph_collection(
            response=response,
            resource_name=resource_name,
        )

    @staticmethod
    def _extract_graph_collection(
        response: dict[str, Any],
        resource_name: str,
    ) -> list[dict[str, Any]]:
        """
        Validate and return the object collection from a Graph response.
        """

        records = response.get("value", [])

        if not isinstance(records, list):
            raise ValueError(
                f"Microsoft Graph {resource_name} response did not "
                "contain a valid 'value' collection."
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
            source_identifier = self._clean_string(
                user.get("id")
            )
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
        provider-neutral identity correlation reference.
        """

        accounts: list[dict[str, Any]] = []

        for user in graph_users:
            source_identifier = self._clean_string(
                user.get("id")
            )
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
                    "account_type": (
                        self._account_type_from_user_type(
                            user.get("userType")
                        )
                    ),
                    "status": self._status_from_account_enabled(
                        user.get("accountEnabled")
                    ),
                    "system_name": self.SYSTEM_NAME,
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": source_identifier,
                    "identity_source_system": self.SYSTEM_NAME,
                    "identity_source_identifier": (
                        source_identifier
                    ),
                    "confidence_score": 100,
                }
            )

        return accounts

    def _build_live_groups(
        self,
        graph_groups: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Translate Microsoft Graph groups into canonical USOP group records.

        Microsoft-specific group properties are translated into a stable
        provider-neutral group_type value.
        """

        groups: list[dict[str, Any]] = []

        for group in graph_groups:
            source_identifier = self._clean_string(
                group.get("id")
            )
            display_name = self._clean_string(
                group.get("displayName")
            )

            if not source_identifier or not display_name:
                continue

            groups.append(
                {
                    "name": display_name,
                    "display_name": display_name,
                    "group_type": (
                        self._group_type_from_graph_group(
                            group
                        )
                    ),
                    "status": "Active",
                    "system_name": self.SYSTEM_NAME,
                    "description": self._clean_string(
                        group.get("description")
                    ),
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": source_identifier,
                    "confidence_score": 100,
                }
            )

        return groups

    def _collect_and_build_live_memberships(
        self,
        graph_groups: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Collect and translate direct group membership relationships.

        Each canonical membership identifies both ends of the relationship
        using provider source references:

        - subject_source_system
        - subject_source_identifier
        - group_source_system
        - group_source_identifier

        Reconciliation will resolve those references into canonical database
        identifiers in the persistence milestone.
        """

        memberships: list[dict[str, Any]] = []

        for group in graph_groups:
            group_source_identifier = self._clean_string(
                group.get("id")
            )

            if not group_source_identifier:
                continue

            graph_members = (
                self._collect_live_group_member_records(
                    group
                )
            )

            for member in graph_members:
                membership = self._build_live_membership(
                    member=member,
                    group_source_identifier=(
                        group_source_identifier
                    ),
                )

                if membership:
                    memberships.append(
                        membership
                    )

        return memberships

    def _build_live_membership(
        self,
        member: dict[str, Any],
        group_source_identifier: str,
    ) -> dict[str, Any] | None:
        """
        Translate one Graph group-member edge into a canonical relationship.

        Unsupported Graph member types are skipped rather than being forced
        into an incorrect principal category.
        """

        subject_source_identifier = self._clean_string(
            member.get("id")
        )
        subject_type = self._principal_type_from_graph_member(
            member
        )

        if (
            not subject_source_identifier
            or subject_type is None
        ):
            return None

        source_identifier = (
            f"{group_source_identifier}:"
            f"{subject_source_identifier}:direct"
        )

        return {
            "subject_type": subject_type.value,
            "subject_source_system": self.SYSTEM_NAME,
            "subject_source_identifier": (
                subject_source_identifier
            ),
            "group_source_system": self.SYSTEM_NAME,
            "group_source_identifier": (
                group_source_identifier
            ),
            "membership_type": "Direct",
            "status": "Active",
            "source_system": self.SYSTEM_NAME,
            "source_identifier": source_identifier,
            "confidence_score": 100,
        }

    def collect_live_users(
        self,
    ) -> list[dict[str, Any]]:
        """
        Collect live identities derived from Microsoft Entra users.
        """

        graph_users = self._collect_live_user_records()

        return self._build_live_identities(
            graph_users
        )

    def collect_live_accounts(
        self,
    ) -> list[dict[str, Any]]:
        """
        Collect live accounts derived from Microsoft Entra users.
        """

        graph_users = self._collect_live_user_records()

        return self._build_live_accounts(
            graph_users
        )

    def collect_live_groups(
        self,
    ) -> list[dict[str, Any]]:
        """
        Collect live groups derived from Microsoft Entra groups.
        """

        graph_groups = self._collect_live_group_records()

        return self._build_live_groups(
            graph_groups
        )

    def collect_live_memberships(
        self,
    ) -> list[dict[str, Any]]:
        """
        Collect direct live Microsoft Entra group memberships.
        """

        graph_groups = self._collect_live_group_records()

        return self._collect_and_build_live_memberships(
            graph_groups
        )

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
            "role_assignments": (
                self.collect_demo_role_assignments()
            ),
        }

    def collect_demo_users(
        self,
    ) -> list[dict[str, Any]]:
        return [
            {
                "display_name": "Marvin Dewitt",
                "identity_class": "Person",
                "primary_email": "mgeoffdewitt@gmail.com",
                "status": "Active",
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-user-marvin-dewitt"
                ),
                "confidence_score": 100,
            }
        ]

    def collect_demo_accounts(
        self,
    ) -> list[dict[str, Any]]:
        return [
            {
                "username": "mdewitt",
                "display_name": "Marvin Dewitt",
                "account_type": "User",
                "status": "Active",
                "system_name": self.SYSTEM_NAME,
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-account-mdewitt"
                ),
                "identity_source_system": self.SYSTEM_NAME,
                "identity_source_identifier": (
                    "demo-user-marvin-dewitt"
                ),
                "confidence_score": 100,
            }
        ]

    def collect_demo_groups(
        self,
    ) -> list[dict[str, Any]]:
        return [
            {
                "name": "entra-security-admins",
                "display_name": (
                    "Entra Security Administrators"
                ),
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

    def collect_demo_roles(
        self,
    ) -> list[dict[str, Any]]:
        return [
            {
                "name": "Global Reader",
                "display_name": "Global Reader",
                "role_type": "Directory",
                "status": "Active",
                "system_name": self.SYSTEM_NAME,
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-role-global-reader"
                ),
                "confidence_score": 100,
            }
        ]

    def collect_demo_memberships(
        self,
    ) -> list[dict[str, Any]]:
        return [
            {
                "subject_type": (
                    PrincipalType.ACCOUNT.value
                ),
                "subject_source_system": self.SYSTEM_NAME,
                "subject_source_identifier": (
                    "demo-account-mdewitt"
                ),
                "group_source_system": self.SYSTEM_NAME,
                "group_source_identifier": (
                    "demo-group-entra-security-admins"
                ),
                "membership_type": "Direct",
                "status": "Active",
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-membership-mdewitt-security-admins"
                ),
                "confidence_score": 100,
            }
        ]

    def collect_demo_role_assignments(
        self,
    ) -> list[dict[str, Any]]:
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
            message=(
                "Microsoft Entra collection completed."
            ),
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
    def _clean_string(
        value: Any,
    ) -> str | None:
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
        """

        normalized_user_type = str(
            user_type or ""
        ).strip().lower()

        if normalized_user_type == "guest":
            return "External"

        return "User"

    @staticmethod
    def _principal_type_from_graph_member(
        member: dict[str, Any],
    ) -> PrincipalType | None:
        """
        Translate a Microsoft Graph directory object type into a canonical
        PrincipalType.

        Unknown directory object types are intentionally not guessed.
        """

        odata_type = str(
            member.get("@odata.type") or ""
        ).strip().lower()

        if odata_type.endswith(".user"):
            return PrincipalType.ACCOUNT

        if odata_type.endswith(".serviceprincipal"):
            return PrincipalType.SERVICE_PRINCIPAL

        if odata_type.endswith(".device"):
            return PrincipalType.DEVICE

        if odata_type.endswith(".group"):
            return PrincipalType.GROUP

        if odata_type.endswith(".orgcontact"):
            return PrincipalType.EXTERNAL_PRINCIPAL

        return None

    @staticmethod
    def _group_type_from_graph_group(
        group: dict[str, Any],
    ) -> str:
        """
        Translate Microsoft Graph group properties into a canonical type.
        """

        group_types = group.get("groupTypes") or []

        normalized_group_types = {
            str(value).strip().lower()
            for value in group_types
        }

        security_enabled = (
            group.get("securityEnabled") is True
        )
        mail_enabled = (
            group.get("mailEnabled") is True
        )
        dynamic_membership = (
            "dynamicmembership"
            in normalized_group_types
        )
        unified = (
            "unified"
            in normalized_group_types
        )

        if dynamic_membership and security_enabled:
            return "DynamicSecurity"

        if dynamic_membership and unified:
            return "DynamicCollaboration"

        if unified:
            return "Collaboration"

        if security_enabled and mail_enabled:
            return "MailEnabledSecurity"

        if security_enabled:
            return "Security"

        if mail_enabled:
            return "Distribution"

        return "Group"
