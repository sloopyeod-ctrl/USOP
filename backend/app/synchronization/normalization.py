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
                    "source": connector_name,
                }
            )

        return normalized