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
        risk_score = 0

        identity = graph["identity"]

        nodes.append({
            "id": identity["id"],
            "type": "identity",
            "label": identity["display_name"],
            "risk_contribution": 0,
        })

        for account in graph["accounts"]:
            contribution = self._account_risk(account)
            risk_score += contribution

            nodes.append({
                "id": account["id"],
                "type": "account",
                "label": account["username"],
                "risk_contribution": contribution,
                "details": account,
            })

            edges.append({
                "source": identity["id"],
                "target": account["id"],
                "relationship": "owns_account",
                "risk_contribution": contribution,
            })

        for group in graph["groups"]:
            contribution = self._group_risk(group)
            risk_score += contribution

            nodes.append({
                "id": group["group_id"],
                "type": "group",
                "label": group["group_name"],
                "risk_contribution": contribution,
                "details": group,
            })

            edges.append({
                "source": group["account_id"],
                "target": group["group_id"],
                "relationship": "member_of",
                "risk_contribution": contribution,
            })

        for role in graph["roles"]:
            contribution = self._role_risk(role)
            risk_score += contribution

            nodes.append({
                "id": role["role_id"],
                "type": "role",
                "label": role["role_name"],
                "risk_contribution": contribution,
                "details": role,
            })

            edges.append({
                "source": role["account_id"],
                "target": role["role_id"],
                "relationship": "assigned_role",
                "risk_contribution": contribution,
            })

        return {
            "identity": identity,
            "attack_path": {
                "risk_score": min(risk_score, 100),
                "risk_level": self._risk_level(risk_score),
                "nodes": nodes,
                "edges": edges,
            },
            "recommendations": intelligence["recommendations"],
            "summary": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "highest_risk_node": self._highest_risk_node(nodes),
                "top_remediation": self._top_remediation(intelligence["recommendations"]),
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
        if score >= 60:
            return "High"
        if score >= 30:
            return "Medium"
        return "Low"

    def _highest_risk_node(self, nodes):
        risky_nodes = [node for node in nodes if node.get("risk_contribution", 0) > 0]

        if not risky_nodes:
            return None

        return max(risky_nodes, key=lambda node: node["risk_contribution"])

    def _top_remediation(self, recommendations):
        if not recommendations:
            return None

        return max(recommendations, key=lambda rec: rec.get("risk_reduction", 0))