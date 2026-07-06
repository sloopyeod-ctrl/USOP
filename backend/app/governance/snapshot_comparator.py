class SnapshotComparator:
    @staticmethod
    def compare(old_snapshot: dict | None, new_snapshot: dict | None) -> list[dict]:
        if old_snapshot is None:
            return [
                {
                    "type": "Initial Snapshot",
                    "severity": "Low",
                    "message": "Initial access review snapshot created.",
                }
            ]

        changes = []

        changes.extend(
            SnapshotComparator._compare_named_items(
                old_snapshot.get("accounts", []),
                new_snapshot.get("accounts", []),
                key="username",
                label="Account",
            )
        )

        changes.extend(
            SnapshotComparator._compare_named_items(
                old_snapshot.get("groups", []),
                new_snapshot.get("groups", []),
                key="name",
                label="Group",
            )
        )

        changes.extend(
            SnapshotComparator._compare_named_items(
                old_snapshot.get("roles", []),
                new_snapshot.get("roles", []),
                key="name",
                label="Role",
            )
        )

        changes.extend(
            SnapshotComparator._compare_authentication(
                old_snapshot.get("accounts", []),
                new_snapshot.get("accounts", []),
            )
        )

        return changes

    @staticmethod
    def _compare_named_items(
        old_items: list[dict],
        new_items: list[dict],
        key: str,
        label: str,
    ) -> list[dict]:
        changes = []

        old_map = {item.get(key): item for item in old_items if item.get(key)}
        new_map = {item.get(key): item for item in new_items if item.get(key)}

        old_keys = set(old_map.keys())
        new_keys = set(new_map.keys())

        for added in sorted(new_keys - old_keys):
            item = new_map[added]
            severity = "High" if item.get("privilege_level") in ["Privileged", "Admin", "High"] else "Moderate"

            changes.append(
                {
                    "type": f"{label} Added",
                    "severity": severity,
                    "message": f"Added {label.lower()} {added}.",
                }
            )

        for removed in sorted(old_keys - new_keys):
            changes.append(
                {
                    "type": f"{label} Removed",
                    "severity": "Moderate",
                    "message": f"Removed {label.lower()} {removed}.",
                }
            )

        return changes

    @staticmethod
    def _compare_authentication(
        old_accounts: list[dict],
        new_accounts: list[dict],
    ) -> list[dict]:
        changes = []

        old_map = {
            account.get("username"): account
            for account in old_accounts
            if account.get("username")
        }
        new_map = {
            account.get("username"): account
            for account in new_accounts
            if account.get("username")
        }

        for username in sorted(set(old_map.keys()) & set(new_map.keys())):
            old_account = old_map[username]
            new_account = new_map[username]

            fields = [
                "authentication_method",
                "authentication_provider",
                "authentication_strength",
                "mfa_enabled",
            ]

            for field in fields:
                if old_account.get(field) != new_account.get(field):
                    changes.append(
                        {
                            "type": "Authentication Changed",
                            "severity": "High" if field == "mfa_enabled" else "Moderate",
                            "message": (
                                f"{field} changed for {username}: "
                                f"{old_account.get(field)} -> {new_account.get(field)}."
                            ),
                        }
                    )

        return changes