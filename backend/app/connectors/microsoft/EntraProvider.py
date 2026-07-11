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
    - direct group memberships
    - assigned directory role definitions
    - active directory role assignments
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
                    "roles",
                    "role_assignments",
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

        Users are translated into both canonical identities and provider
        accounts from one Graph request.

        Groups are reused for both group collection and direct membership
        collection.

        Role collection is assignment-driven. The provider retrieves active
        role assignments first and then fetches only the role definitions and
        principals referenced by those assignments. The complete Microsoft
        directory role catalog is intentionally not collected.

        Relationship records contain provider source references rather than
        PostgreSQL identifiers. Canonical IDs are resolved during
        reconciliation.
        """

        graph_users = self._collect_live_user_records()
        graph_groups = self._collect_live_group_records()

        role_collection = (
            self._collect_live_role_assignment_bundle()
        )

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
            "roles": role_collection["roles"],
            "memberships": (
                self._collect_and_build_live_memberships(
                    graph_groups
                )
            ),
            "role_assignments": (
                role_collection["role_assignments"]
            ),
        }

    def _collect_live_user_records(
        self,
    ) -> list[dict[str, Any]]:
        """
        Retrieve Microsoft Graph users needed by identity and account
        translations.

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
        Retrieve Microsoft Graph groups needed by group and membership
        translations.

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

        Transitive membership is intentionally not collected in this
        capability.
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
            f"group members for "
            f"{group_name or group_identifier}"
        )

        return self._extract_graph_collection(
            response=response,
            resource_name=resource_name,
        )

    def _collect_live_role_assignment_records(
        self,
    ) -> list[dict[str, Any]]:
        """
        Retrieve active Microsoft Entra directory role assignments.

        No expansion or selection parameters are used because support for
        combined expansions varies on the Graph collection endpoint.

        Role definitions and principals are resolved separately by their
        stable provider identifiers.
        """

        response = self.graph.get(
            "/roleManagement/directory/roleAssignments"
        )

        return self._extract_graph_collection(
            response=response,
            resource_name="directory role assignments",
        )

    def _collect_live_role_definition_record(
        self,
        role_definition_identifier: str,
    ) -> dict[str, Any]:
        """
        Retrieve one directory role definition referenced by an assignment.
        """

        response = self.graph.get(
            "/roleManagement/directory/"
            f"roleDefinitions/{role_definition_identifier}"
        )

        if not isinstance(response, dict):
            raise ValueError(
                "Microsoft Graph directory role definition "
                "response was not an object."
            )

        return response

    def _collect_live_directory_object_record(
        self,
        principal_identifier: str,
    ) -> dict[str, Any]:
        """
        Retrieve one directory principal referenced by a role assignment.

        The directory object type is retained so the connector can translate
        the principal into the canonical PrincipalType vocabulary.
        """

        response = self.graph.get(
            f"/directoryObjects/{principal_identifier}"
        )

        if not isinstance(response, dict):
            raise ValueError(
                "Microsoft Graph directory object response "
                "was not an object."
            )

        return response

    def _collect_live_role_assignment_bundle(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Collect assigned role definitions and active role assignments.

        Assignment-driven collection prevents USOP from importing every
        available Microsoft directory role definition when most are not
        operationally relevant to the tenant.

        The returned role-assignment records contain provider references.
        They do not contain PostgreSQL IDs.
        """

        graph_assignments = (
            self._collect_live_role_assignment_records()
        )

        role_definition_identifiers = {
            role_definition_identifier
            for assignment in graph_assignments
            if (
                role_definition_identifier
                := self._clean_string(
                    assignment.get("roleDefinitionId")
                )
            )
        }

        principal_identifiers = {
            principal_identifier
            for assignment in graph_assignments
            if (
                principal_identifier
                := self._clean_string(
                    assignment.get("principalId")
                )
            )
        }

        graph_role_definitions: dict[
            str,
            dict[str, Any],
        ] = {}

        for role_definition_identifier in sorted(
            role_definition_identifiers
        ):
            graph_role_definitions[
                role_definition_identifier
            ] = (
                self._collect_live_role_definition_record(
                    role_definition_identifier
                )
            )

        graph_principals: dict[
            str,
            dict[str, Any],
        ] = {}

        for principal_identifier in sorted(
            principal_identifiers
        ):
            graph_principals[
                principal_identifier
            ] = (
                self._collect_live_directory_object_record(
                    principal_identifier
                )
            )

        roles = self._build_live_roles(
            graph_role_definitions
        )

        role_assignments = (
            self._build_live_role_assignments(
                graph_assignments=graph_assignments,
                graph_role_definitions=(
                    graph_role_definitions
                ),
                graph_principals=graph_principals,
            )
        )

        return {
            "roles": roles,
            "role_assignments": role_assignments,
        }

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
                    "status": (
                        self._status_from_account_enabled(
                            user.get("accountEnabled")
                        )
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
                    "status": (
                        self._status_from_account_enabled(
                            user.get("accountEnabled")
                        )
                    ),
                    "system_name": self.SYSTEM_NAME,
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": source_identifier,
                    "identity_source_system": (
                        self.SYSTEM_NAME
                    ),
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
        Translate Microsoft Graph groups into canonical group records.
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
        """

        subject_source_identifier = self._clean_string(
            member.get("id")
        )
        subject_type = (
            self._principal_type_from_graph_object(
                member
            )
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

    def _build_live_roles(
        self,
        graph_role_definitions: dict[
            str,
            dict[str, Any],
        ],
    ) -> list[dict[str, Any]]:
        """
        Translate only role definitions referenced by active assignments.

        The complete Microsoft Entra role-definition catalog is intentionally
        excluded from operational collection.
        """

        roles: list[dict[str, Any]] = []

        for (
            expected_identifier,
            role_definition,
        ) in sorted(
            graph_role_definitions.items()
        ):
            source_identifier = self._clean_string(
                role_definition.get("id")
            ) or expected_identifier

            display_name = self._clean_string(
                role_definition.get("displayName")
            )

            if not source_identifier or not display_name:
                continue

            roles.append(
                {
                    "name": display_name,
                    "display_name": display_name,
                    "role_type": "Directory",
                    "status": (
                        "Inactive"
                        if role_definition.get("isEnabled")
                        is False
                        else "Active"
                    ),
                    "system_name": self.SYSTEM_NAME,
                    "description": self._clean_string(
                        role_definition.get("description")
                    ),
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": source_identifier,
                    "confidence_score": 100,
                }
            )

        return roles

    def _build_live_role_assignments(
        self,
        graph_assignments: list[dict[str, Any]],
        graph_role_definitions: dict[
            str,
            dict[str, Any],
        ],
        graph_principals: dict[
            str,
            dict[str, Any],
        ],
    ) -> list[dict[str, Any]]:
        """
        Translate Graph role assignments into canonical relationships.

        assignment_type is intentionally recorded as Direct rather than
        Permanent. The roleAssignments endpoint establishes the active
        principal-to-role edge but does not provide sufficient schedule
        evidence to classify every assignment as permanently active.

        PIM eligibility, schedule instances, and activation history remain
        separate capabilities.
        """

        role_assignments: list[dict[str, Any]] = []

        for assignment in graph_assignments:
            assignment_identifier = self._clean_string(
                assignment.get("id")
            )
            principal_identifier = self._clean_string(
                assignment.get("principalId")
            )
            role_definition_identifier = (
                self._clean_string(
                    assignment.get(
                        "roleDefinitionId"
                    )
                )
            )

            if (
                not assignment_identifier
                or not principal_identifier
                or not role_definition_identifier
            ):
                continue

            principal = graph_principals.get(
                principal_identifier,
                {},
            )

            role_definition = (
                graph_role_definitions.get(
                    role_definition_identifier,
                    {},
                )
            )

            subject_type = (
                self._principal_type_from_graph_object(
                    principal
                )
            )

            resolved_role_identifier = (
                self._clean_string(
                    role_definition.get("id")
                )
                or role_definition_identifier
            )

            if (
                subject_type is None
                or not resolved_role_identifier
            ):
                continue

            role_assignments.append(
                {
                    "subject_type": subject_type.value,
                    "subject_source_system": (
                        self.SYSTEM_NAME
                    ),
                    "subject_source_identifier": (
                        principal_identifier
                    ),
                    "role_source_system": (
                        self.SYSTEM_NAME
                    ),
                    "role_source_identifier": (
                        resolved_role_identifier
                    ),
                    "assignment_type": "Direct",
                    "status": "Active",
                    "directory_scope": (
                        self._clean_string(
                            assignment.get(
                                "directoryScopeId"
                            )
                        )
                    ),
                    "application_scope": (
                        self._clean_string(
                            assignment.get(
                                "appScopeId"
                            )
                        )
                    ),
                    "source_system": self.SYSTEM_NAME,
                    "source_identifier": (
                        assignment_identifier
                    ),
                    "confidence_score": 100,
                }
            )

        return role_assignments

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

    def collect_live_roles(
        self,
    ) -> list[dict[str, Any]]:
        """
        Collect role definitions referenced by active assignments.
        """

        collection = (
            self._collect_live_role_assignment_bundle()
        )

        return collection["roles"]

    def collect_live_role_assignments(
        self,
    ) -> list[dict[str, Any]]:
        """
        Collect active Microsoft Entra role assignments.
        """

        collection = (
            self._collect_live_role_assignment_bundle()
        )

        return collection["role_assignments"]

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
                "identity_source_system": (
                    self.SYSTEM_NAME
                ),
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
                "subject_source_system": (
                    self.SYSTEM_NAME
                ),
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
                "subject_type": (
                    PrincipalType.ACCOUNT.value
                ),
                "subject_source_system": (
                    self.SYSTEM_NAME
                ),
                "subject_source_identifier": (
                    "demo-account-mdewitt"
                ),
                "role_source_system": self.SYSTEM_NAME,
                "role_source_identifier": (
                    "demo-role-global-reader"
                ),
                "assignment_type": "Direct",
                "status": "Active",
                "directory_scope": "/",
                "application_scope": None,
                "source_system": self.SYSTEM_NAME,
                "source_identifier": (
                    "demo-role-assignment-mdewitt-global-reader"
                ),
                "confidence_score": 100,
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
        Translate provider account state into canonical status.
        """

        if account_enabled is False:
            return "Inactive"

        return "Active"

    @staticmethod
    def _account_type_from_user_type(
        user_type: Any,
    ) -> str:
        """
        Translate Entra userType into canonical account type.
        """

        normalized_user_type = str(
            user_type or ""
        ).strip().lower()

        if normalized_user_type == "guest":
            return "External"

        return "User"

    @staticmethod
    def _principal_type_from_graph_object(
        graph_object: dict[str, Any],
    ) -> PrincipalType | None:
        """
        Translate a Graph directory object type into PrincipalType.

        Unknown directory object types are intentionally not guessed.
        """

        odata_type = str(
            graph_object.get("@odata.type") or ""
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
        Translate Microsoft Graph group properties into canonical type.
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