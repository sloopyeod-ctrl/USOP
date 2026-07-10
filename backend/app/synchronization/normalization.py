class NormalizationEngine:
    """
    Translate provider collection records into canonical USOP structures.

    Connectors own provider-specific collection and translation. This engine
    applies shared normalization rules before records enter reconciliation.
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
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned or None

    def canonical_key(self, value):
        cleaned = self.clean_string(value)

        if cleaned is None:
            return None

        return cleaned.lower()

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
                    "confidence_score": identity.get(
                        "confidence_score",
                        100,
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
                        account.get("mfa_enabled", False)
                    ),
                    "last_seen_at": account.get(
                        "last_seen_at"
                    ),
                    "confidence_score": account.get(
                        "confidence_score",
                        100,
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
        normalized = []

        for group in groups:
            name = self.clean_string(
                group.get("name")
            )

            if not name:
                continue

            normalized.append(
                {
                    "name": name,
                    "name_key": self.canonical_key(name),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_roles(
        self,
        connector_name,
        roles,
    ):
        normalized = []

        for role in roles:
            name = self.clean_string(
                role.get("name")
            )

            if not name:
                continue

            normalized.append(
                {
                    "name": name,
                    "name_key": self.canonical_key(name),
                    "system_name": self.clean_string(
                        role.get(
                            "system_name",
                            "Entra ID",
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
        normalized = []

        for membership in memberships:
            username = self.clean_string(
                membership.get("username")
            )
            group_name = self.clean_string(
                membership.get("group_name")
            )

            if not username or not group_name:
                continue

            normalized.append(
                {
                    "username": username,
                    "group_name": group_name,
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_role_assignments(
        self,
        connector_name,
        assignments,
    ):
        normalized = []

        for assignment in assignments:
            username = self.clean_string(
                assignment.get("username")
            )
            role_name = self.clean_string(
                assignment.get("role_name")
            )

            if not username or not role_name:
                continue

            normalized.append(
                {
                    "username": username,
                    "role_name": role_name,
                    "source": connector_name,
                }
            )

        return normalized