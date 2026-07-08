from sqlalchemy.orm import Session

from app.graph.identity_graph_service import IdentityGraphService
from app.intelligence.identity_intelligence_service import IdentityIntelligenceService


class AttackPathService:
    def __init__(self, db: Session):
        self.db = db
        self.graph_service = IdentityGraphService(db)
        self.intelligence_service = IdentityIntelligenceService(db)

    def get_attack_path(self, identity_id: str):
        graph = self.graph_service.get_identity_graph(identity_id)
        intelligence = self.intelligence_service.get_identity_intelligence(identity_id)

        if graph is None or intelligence is None:
            return None

        nodes = []
        edges = []

        identity = graph["identity"]
        recommendations = intelligence["recommendations"]
        findings = intelligence["risk"]["findings"]

        nodes.append({
            "id": identity["id"],
            "type": "identity",
            "label": identity["display_name"],
            "risk_contribution": 0,
            "risk_level": "Low",
            "criticality": 0,
            "blast_radius": len(graph["accounts"]) + len(graph["groups"]) + len(graph["roles"]),
            "recommendation_count": len(recommendations),
            "details": identity,
        })

        for account in graph["accounts"]:
            contribution = self._account_risk(account)
            account_recommendations = self._related_recommendations(
                recommendations,
                account.get("username"),
            )

            nodes.append({
                "id": account["id"],
                "type": "account",
                "label": account["username"],
                "risk_contribution": contribution,
                "risk_level": self._risk_level(contribution),
                "criticality": min(contribution * 2, 100),
                "blast_radius": self._account_blast_radius(account, graph),
                "recommendation_count": len(account_recommendations),
                "details": account,
            })

            edges.append({
                "source": identity["id"],
                "target": account["id"],
                "relationship": "owns_account",
                "risk_contribution": contribution,
                "risk_level": self._risk_level(contribution),
            })

        for group in graph["groups"]:
            contribution = self._group_risk(group)
            group_recommendations = self._related_recommendations(
                recommendations,
                group.get("group_name"),
            )

            nodes.append({
                "id": group["group_id"],
                "type": "group",
                "label": group["group_name"],
                "risk_contribution": contribution,
                "risk_level": self._risk_level(contribution),
                "criticality": min(contribution * 2, 100),
                "blast_radius": self._group_blast_radius(group, graph),
                "recommendation_count": len(group_recommendations),
                "details": group,
            })

            edges.append({
                "source": group["account_id"],
                "target": group["group_id"],
                "relationship": "member_of",
                "risk_contribution": contribution,
                "risk_level": self._risk_level(contribution),
            })

        for role in graph["roles"]:
            contribution = self._role_risk(role)
            role_recommendations = self._related_recommendations(
                recommendations,
                role.get("role_name"),
            )

            nodes.append({
                "id": role["role_id"],
                "type": "role",
                "label": role["role_name"],
                "risk_contribution": contribution,
                "risk_level": self._risk_level(contribution),
                "criticality": min(contribution * 2, 100),
                "blast_radius": self._role_blast_radius(role, graph),
                "recommendation_count": len(role_recommendations),
                "details": role,
            })

            edges.append({
                "source": role["account_id"],
                "target": role["role_id"],
                "relationship": "assigned_role",
                "risk_contribution": contribution,
                "risk_level": self._risk_level(contribution),
            })

        total_risk = sum(node["risk_contribution"] for node in nodes)

        return {
            "identity": identity,
            "attack_path": {
                "risk_score": min(total_risk, 100),
                "risk_level": self._risk_level(total_risk),
                "nodes": nodes,
                "edges": edges,
            },
            "recommendations": recommendations,
            "findings": findings,
            "summary": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "highest_risk_node": self._highest_risk_node(nodes),
                "top_remediation": self._top_remediation(recommendations),
                "blast_radius": self._blast_radius(nodes),
                "critical_paths": self._critical_paths(nodes, edges),
            },
        }

    def _account_risk(self, account):
        score = 5

        if account.get("privilege_level") == "Privileged":
            score += 25

        if account.get("mfa_enabled") is False:
            score += 20

        if account.get("account_type") == "Admin":
            score += 15

        return score

    def _group_risk(self, group):
        score = 10

        if group.get("privilege_level") == "Privileged":
            score += 25

        return score

    def _role_risk(self, role):
        score = 10

        if role.get("privilege_level") in ["Privileged", "Admin", "Owner"]:
            score += 30

        if role.get("privilege_level") == "ReadOnly":
            score += 5

        return score

    def _risk_level(self, score):
        if score >= 80:
            return "Critical"
        if score >= 50:
            return "High"
        if score >= 25:
            return "Medium"
        return "Low"

    def _related_recommendations(self, recommendations, value):
        if not value:
            return []

        value = value.lower()

        return [
            rec for rec in recommendations
            if value in f"{rec.get('title', '')} {rec.get('description', '')}".lower()
        ]

    def _account_blast_radius(self, account, graph):
        account_id = account.get("id")

        groups = [
            group for group in graph["groups"]
            if group.get("account_id") == account_id
        ]

        roles = [
            role for role in graph["roles"]
            if role.get("account_id") == account_id
        ]

        return len(groups) + len(roles)

    def _group_blast_radius(self, group, graph):
        group_id = group.get("group_id")

        related_accounts = [
            item for item in graph["groups"]
            if item.get("group_id") == group_id
        ]

        return len(related_accounts)

    def _role_blast_radius(self, role, graph):
        role_id = role.get("role_id")

        related_accounts = [
            item for item in graph["roles"]
            if item.get("role_id") == role_id
        ]

        return len(related_accounts)

    def _highest_risk_node(self, nodes):
        risky_nodes = [
            node for node in nodes
            if node.get("risk_contribution", 0) > 0
        ]

        if not risky_nodes:
            return None

        return max(risky_nodes, key=lambda node: node["risk_contribution"])

    def _top_remediation(self, recommendations):
        if not recommendations:
            return None

        return max(
            recommendations,
            key=lambda rec: rec.get("risk_reduction", 0),
        )

    def _blast_radius(self, nodes):
        return {
            "total_objects": len(nodes),
            "critical_objects": len([
                node for node in nodes
                if node.get("risk_level") == "Critical"
            ]),
            "high_risk_objects": len([
                node for node in nodes
                if node.get("risk_level") == "High"
            ]),
            "medium_risk_objects": len([
                node for node in nodes
                if node.get("risk_level") == "Medium"
            ]),
        }

    def _critical_paths(self, nodes, edges):
        node_lookup = {
            node["id"]: node
            for node in nodes
        }

        critical_edges = [
            edge for edge in edges
            if edge.get("risk_level") in ["Critical", "High"]
        ]

        paths = []

        for edge in critical_edges:
            source = node_lookup.get(edge["source"])
            target = node_lookup.get(edge["target"])

            if source and target:
                paths.append({
                    "source": source["label"],
                    "target": target["label"],
                    "relationship": edge["relationship"],
                    "risk_contribution": edge["risk_contribution"],
                    "risk_level": edge["risk_level"],
                })

        return paths