class NormalizationEngine:

    def normalize(self, connector_name: str, data: dict):
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

    def clean_string(self, value):
        if value is None:
            return None

        return str(value).strip()

    def canonical_key(self, value):
        cleaned = self.clean_string(value)

        if cleaned is None:
            return None

        return cleaned.lower()

    def normalize_identities(self, connector_name, identities):
        normalized = []

        for identity in identities:
            normalized.append(
                {
                    "display_name": identity.get("display_name"),
                    "primary_email": identity.get("primary_email"),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_accounts(self, connector_name, accounts):
        normalized = []

        for account in accounts:
            username = self.clean_string(account.get("username"))

            normalized.append(
                {
                    "username": username,
                    "username_key": self.canonical_key(username),
                    "system_name": self.clean_string(account.get("system_name")),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_groups(self, connector_name, groups):
        normalized = []

        for group in groups:
            name = self.clean_string(group.get("name"))

            normalized.append(
                {
                    "name": name,
                    "name_key": self.canonical_key(name),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_roles(self, connector_name, roles):
        normalized = []

        for role in roles:
            name = self.clean_string(role.get("name"))

            normalized.append(
                {
                    "name": name,
                    "name_key": self.canonical_key(name),
                    "system_name": self.clean_string(role.get("system_name", "Entra ID")),
                    "source": connector_name,
                }
            )

        return normalized
    
    def normalize_memberships(self, connector_name, memberships):
        normalized = []

        for membership in memberships:
            normalized.append(
                {
                    "username": membership["username"],
                    "group_name": membership["group_name"],
                    "source": connector_name,
                }
            )

        return normalized
    
    def normalize_role_assignments(self, connector_name, assignments):
        normalized = []

        for assignment in assignments:
            normalized.append(
                {
                    "username": assignment["username"],
                    "role_name": assignment["role_name"],
                    "source": connector_name,
                }
            )

        return normalized