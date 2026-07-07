from app.graph.identity_graph_service import IdentityGraphService
from app.graph.graph_snapshot_service import GraphSnapshotService


class GraphDifferenceEngine:
    def __init__(self, db):
        self.graph_service = IdentityGraphService(db)
        self.snapshot_service = GraphSnapshotService(db)
        
    def compare(self, before: dict, after: dict):
        before_groups = {
            group["group_name"]
            for group in before.get("groups", [])
        }

        after_groups = {
            group["group_name"]
            for group in after.get("groups", [])
        }

        before_roles = {
            role["role_name"]
            for role in before.get("roles", [])
        }

        after_roles = {
            role["role_name"]
            for role in after.get("roles", [])
        }

        before_accounts = {
            account["username"]
            for account in before.get("accounts", [])
        }

        after_accounts = {
            account["username"]
            for account in after.get("accounts", [])
        }

        return {
            "added_accounts": sorted(after_accounts - before_accounts),
            "removed_accounts": sorted(before_accounts - after_accounts),

            "added_groups": sorted(after_groups - before_groups),
            "removed_groups": sorted(before_groups - after_groups),

            "added_roles": sorted(after_roles - before_roles),
            "removed_roles": sorted(before_roles - after_roles),
        }