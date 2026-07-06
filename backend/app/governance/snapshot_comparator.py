class SnapshotComparator:

    @staticmethod
    def compare(old_snapshot: dict | None, new_snapshot: dict | None) -> list[str]:
        """
        Compare two identity snapshots and return a list of human-readable changes.
        """

        if old_snapshot is None:
            return ["Initial Snapshot Created"]

        changes = []

        if old_snapshot.get("accounts") != new_snapshot.get("accounts"):
            changes.append("Accounts changed")

        if old_snapshot.get("groups") != new_snapshot.get("groups"):
            changes.append("Group memberships changed")

        if old_snapshot.get("roles") != new_snapshot.get("roles"):
            changes.append("Role assignments changed")

        return changes