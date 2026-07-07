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
            normalized.append(
                {
                    "username": account.get("username"),
                    "system_name": account.get("system_name"),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_groups(self, connector_name, groups):
        normalized = []

        for group in groups:
            normalized.append(
                {
                    "name": group.get("name"),
                    "source": connector_name,
                }
            )

        return normalized

    def normalize_roles(self, connector_name, roles):
        normalized = []

        for role in roles:
            normalized.append(
                {
                    "name": role.get("name"),
                    "system_name": role.get("system_name", "Entra ID"),
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