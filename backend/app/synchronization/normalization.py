from app.domain.principal_type import PrincipalType
from app.domain.role_type import RoleType


class NormalizationEngine:
    """
    Translate provider collection records into canonical USOP structures.

    Connectors own provider-specific collection and translation. This engine
    applies shared normalization and validation rules before records enter
    reconciliation.

    Normalization preserves provider identity. Reconciliation resolves
    provider references into canonical database identifiers.
    """

    def normalize(
        self,
        connector_name: str,
        data: dict,
    ) -> dict:
        return {
            "identities": self.normalize_identities(
                connector_name,
                data.get("identities", []),
            ),
            "accounts": self.normalize_accounts(
                connector_name,
                data.get("accounts", []),
            ),
            "groups": self.normalize_groups(
                connector_name,
                data.get("groups", []),
            ),
            "roles": self.normalize_roles(
                connector_name,
                data.get("roles", []),
            ),
            "memberships": self.normalize_memberships(
                connector_name,
                data.get("memberships", []),
            ),
            "role_assignments": self.normalize_role_assignments(
                connector_name,
                data.get("role_assignments", []),
            ),
        }

    @staticmethod
    def clean_string(value):
        """
        Convert a value into a trimmed string.

        Empty values are normalized to None.
        """

        if value is None:
            return None

        cleaned = str(value).strip()

        return cleaned or None

    def canonical_key(self, value):
        """
        Produce a case-insensitive comparison key.
        """

        cleaned = self.clean_string(value)

        if cleaned is None:
            return None

        return cleaned.lower()

    @staticmethod
    def normalize_confidence_score(
        value,
        default: int = 100,
    ) -> int:
        """
        Normalize a confidence score into the supported range of 0 to 100.
        """

        try:
            score = int(value)
        except (TypeError, ValueError):
            return default

        return max(0, min(score, 100))

    def normalize_identities(
        self,
        connector_name,
        identities,
    ):
        normalized = []

        for identity in identities:
            display_name = self.clean_string(
                identity.get("display_name")
            )
            primary_email = self.clean_string(
                identity.get("primary_email")
            )

            if not display_name:
                continue

            normalized.append(
                {
                    "display_name": display_name,
                    "identity_class": self.clean_string(
                        identity.get(
                            "identity_class",
                            "Person",
                        )
                    ),
                    "primary_email": primary_email,
                    "status": self.clean_string(
                        identity.get(
                            "status",
                            "Active",
                        )
                    ),
                    "source_system": self.clean_string(
                        identity.get(
                            "source_system",
                            connector_name,
                        )
                    ),
                    "source_identifier": self.clean_string(
                        identity.get("source_identifier")
                    ),
                    "confidence_score": (
                        self.normalize_confidence_score(
                            identity.get(
                                "confidence_score",
                                100,
                            )
                        )
                    ),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_accounts(
        self,
        connector_name,
        accounts,
    ):
        normalized = []

        for account in accounts:
            username = self.clean_string(
                account.get("username")
            )
            system_name = self.clean_string(
                account.get("system_name")
            )

            if not username or not system_name:
                continue

            normalized.append(
                {
                    "username": username,
                    "username_key": self.canonical_key(
                        username
                    ),
                    "display_name": self.clean_string(
                        account.get("display_name")
                    ),
                    "account_type": self.clean_string(
                        account.get(
                            "account_type",
                            "User",
                        )
                    ),
                    "status": self.clean_string(
                        account.get(
                            "status",
                            "Active",
                        )
                    ),
                    "system_name": system_name,
                    "source_system": self.clean_string(
                        account.get(
                            "source_system",
                            connector_name,
                        )
                    ),
                    "source_identifier": self.clean_string(
                        account.get("source_identifier")
                    ),
                    "identity_source_system": self.clean_string(
                        account.get(
                            "identity_source_system"
                        )
                    ),
                    "identity_source_identifier": self.clean_string(
                        account.get(
                            "identity_source_identifier"
                        )
                    ),
                    "privilege_level": self.clean_string(
                        account.get("privilege_level")
                    ),
                    "authentication_method": self.clean_string(
                        account.get(
                            "authentication_method"
                        )
                    ),
                    "authentication_strength": self.clean_string(
                        account.get(
                            "authentication_strength"
                        )
                    ),
                    "authentication_provider": self.clean_string(
                        account.get(
                            "authentication_provider"
                        )
                    ),
                    "mfa_enabled": bool(
                        account.get(
                            "mfa_enabled",
                            False,
                        )
                    ),
                    "last_seen_at": account.get(
                        "last_seen_at"
                    ),
                    "confidence_score": (
                        self.normalize_confidence_score(
                            account.get(
                                "confidence_score",
                                100,
                            )
                        )
                    ),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_groups(
        self,
        connector_name,
        groups,
    ):
        """
        Normalize provider-neutral group collection records.

        Stable provider identifiers are preserved so reconciliation can
        distinguish groups that share a display name across systems or
        providers.
        """

        normalized = []

        for group in groups:
            name = self.clean_string(
                group.get("name")
            )
            system_name = self.clean_string(
                group.get("system_name")
            )

            if not name or not system_name:
                continue

            normalized.append(
                {
                    "name": name,
                    "name_key": self.canonical_key(name),
                    "display_name": self.clean_string(
                        group.get("display_name")
                    ),
                    "group_type": self.clean_string(
                        group.get(
                            "group_type",
                            "Security",
                        )
                    ),
                    "status": self.clean_string(
                        group.get(
                            "status",
                            "Active",
                        )
                    ),
                    "system_name": system_name,
                    "description": self.clean_string(
                        group.get("description")
                    ),
                    "privilege_level": self.clean_string(
                        group.get("privilege_level")
                    ),
                    "source_system": self.clean_string(
                        group.get(
                            "source_system",
                            connector_name,
                        )
                    ),
                    "source_identifier": self.clean_string(
                        group.get("source_identifier")
                    ),
                    "confidence_score": (
                        self.normalize_confidence_score(
                            group.get(
                                "confidence_score",
                                100,
                            )
                        )
                    ),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_roles(
        self,
        connector_name,
        roles,
    ):
        """
        Normalize provider-neutral authorization roles.

        Stable provider identity and descriptive role metadata are preserved
        so reconciliation can distinguish roles with similar names across
        providers and systems.
        """

        normalized = []

        valid_role_types = {
            role_type.value
            for role_type in RoleType
        }

        for role in roles:
            name = self.clean_string(
                role.get("name")
            )
            system_name = self.clean_string(
                role.get("system_name")
            )
            role_type = self.clean_string(
                role.get(
                    "role_type",
                    RoleType.ACCESS.value,
                )
            )

            if (
                not name
                or not system_name
                or role_type not in valid_role_types
            ):
                continue

            normalized.append(
                {
                    "name": name,
                    "name_key": self.canonical_key(name),
                    "display_name": self.clean_string(
                        role.get("display_name")
                    ),
                    "role_type": role_type,
                    "status": self.clean_string(
                        role.get(
                            "status",
                            "Active",
                        )
                    ),
                    "system_name": system_name,
                    "description": self.clean_string(
                        role.get("description")
                    ),
                    "privilege_level": self.clean_string(
                        role.get("privilege_level")
                    ),
                    "source_system": self.clean_string(
                        role.get(
                            "source_system",
                            connector_name,
                        )
                    ),
                    "source_identifier": self.clean_string(
                        role.get("source_identifier")
                    ),
                    "confidence_score": (
                        self.normalize_confidence_score(
                            role.get(
                                "confidence_score",
                                100,
                            )
                        )
                    ),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_memberships(
        self,
        connector_name,
        memberships,
    ):
        """
        Normalize canonical principal-to-group relationships.

        Provider identity is preserved through source-system and
        source-identifier references. Database IDs are intentionally not
        introduced during normalization.

        Legacy username and group-name fields remain supported as controlled
        fallbacks for older demo connectors.
        """

        normalized = []

        for membership in memberships:
            subject_type = self.clean_string(
                membership.get(
                    "subject_type",
                    "Account",
                )
            )

            subject_source_system = self.clean_string(
                membership.get(
                    "subject_source_system"
                )
            )
            subject_source_identifier = self.clean_string(
                membership.get(
                    "subject_source_identifier"
                )
            )

            group_source_system = self.clean_string(
                membership.get(
                    "group_source_system"
                )
            )
            group_source_identifier = self.clean_string(
                membership.get(
                    "group_source_identifier"
                )
            )

            subject_id = self.clean_string(
                membership.get("subject_id")
            )
            group_id = self.clean_string(
                membership.get("group_id")
            )

            username = self.clean_string(
                membership.get("username")
            )
            group_name = self.clean_string(
                membership.get("group_name")
            )

            has_subject_reference = bool(
                subject_id
                or (
                    subject_source_system
                    and subject_source_identifier
                )
                or username
            )

            has_group_reference = bool(
                group_id
                or (
                    group_source_system
                    and group_source_identifier
                )
                or group_name
            )

            if (
                not subject_type
                or not has_subject_reference
                or not has_group_reference
            ):
                continue

            normalized.append(
                {
                    "subject_type": subject_type,
                    "subject_id": subject_id,
                    "subject_source_system": (
                        subject_source_system
                    ),
                    "subject_source_identifier": (
                        subject_source_identifier
                    ),
                    "group_id": group_id,
                    "group_source_system": (
                        group_source_system
                    ),
                    "group_source_identifier": (
                        group_source_identifier
                    ),
                    "username": username,
                    "group_name": group_name,
                    "membership_type": self.clean_string(
                        membership.get(
                            "membership_type",
                            "Direct",
                        )
                    ),
                    "status": self.clean_string(
                        membership.get(
                            "status",
                            "Active",
                        )
                    ),
                    "source_system": self.clean_string(
                        membership.get(
                            "source_system",
                            connector_name,
                        )
                    ),
                    "source_identifier": self.clean_string(
                        membership.get(
                            "source_identifier"
                        )
                    ),
                    "first_seen_at": membership.get(
                        "first_seen_at"
                    ),
                    "last_seen_at": membership.get(
                        "last_seen_at"
                    ),
                    "confidence_score": (
                        self.normalize_confidence_score(
                            membership.get(
                                "confidence_score",
                                100,
                            )
                        )
                    ),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_role_assignments(
        self,
        connector_name,
        assignments,
    ):
        """
        Normalize canonical principal-to-role relationships.

        Provider references are preserved so reconciliation can resolve stable
        canonical account and role IDs. Explicit canonical IDs remain
        supported for internal callers, while username and role-name values
        remain controlled compatibility fallbacks.

        Directory and application scopes are preserved because the same
        principal may hold the same role at different authorization scopes.
        """

        normalized = []

        valid_principal_types = {
            principal_type.value
            for principal_type in PrincipalType
        }

        for assignment in assignments:
            subject_type = self.clean_string(
                assignment.get(
                    "subject_type",
                    PrincipalType.ACCOUNT.value,
                )
            )

            subject_id = self.clean_string(
                assignment.get("subject_id")
            )
            subject_source_system = self.clean_string(
                assignment.get(
                    "subject_source_system"
                )
            )
            subject_source_identifier = self.clean_string(
                assignment.get(
                    "subject_source_identifier"
                )
            )
            username = self.clean_string(
                assignment.get("username")
            )

            role_id = self.clean_string(
                assignment.get("role_id")
            )
            role_source_system = self.clean_string(
                assignment.get(
                    "role_source_system"
                )
            )
            role_source_identifier = self.clean_string(
                assignment.get(
                    "role_source_identifier"
                )
            )
            role_name = self.clean_string(
                assignment.get("role_name")
            )

            has_subject_reference = bool(
                subject_id
                or (
                    subject_source_system
                    and subject_source_identifier
                )
                or username
            )

            has_role_reference = bool(
                role_id
                or (
                    role_source_system
                    and role_source_identifier
                )
                or role_name
            )

            if (
                subject_type not in valid_principal_types
                or not has_subject_reference
                or not has_role_reference
            ):
                continue

            normalized.append(
                {
                    "subject_type": subject_type,
                    "subject_id": subject_id,
                    "subject_source_system": (
                        subject_source_system
                    ),
                    "subject_source_identifier": (
                        subject_source_identifier
                    ),
                    "username": username,
                    "role_id": role_id,
                    "role_source_system": (
                        role_source_system
                    ),
                    "role_source_identifier": (
                        role_source_identifier
                    ),
                    "role_name": role_name,
                    "assignment_type": self.clean_string(
                        assignment.get(
                            "assignment_type",
                            "Direct",
                        )
                    ),
                    "status": self.clean_string(
                        assignment.get(
                            "status",
                            "Active",
                        )
                    ),
                    "directory_scope": self.clean_string(
                        assignment.get(
                            "directory_scope"
                        )
                    ),
                    "application_scope": self.clean_string(
                        assignment.get(
                            "application_scope"
                        )
                    ),
                    "source_system": self.clean_string(
                        assignment.get(
                            "source_system",
                            connector_name,
                        )
                    ),
                    "source_identifier": self.clean_string(
                        assignment.get(
                            "source_identifier"
                        )
                    ),
                    "first_seen_at": assignment.get(
                        "first_seen_at"
                    ),
                    "last_seen_at": assignment.get(
                        "last_seen_at"
                    ),
                    "confidence_score": (
                        self.normalize_confidence_score(
                            assignment.get(
                                "confidence_score",
                                100,
                            )
                        )
                    ),
                    "source": connector_name,
                }
            )

        return normalized