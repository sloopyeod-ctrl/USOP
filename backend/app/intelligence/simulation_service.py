from copy import deepcopy

from app.intelligence.attack_path_service import AttackPathService


class SimulationService:
    """
    Creates temporary attack-path simulations without modifying
    production identity data.
    """

    def __init__(self, db):
        self.db = db
        self.attack_service = AttackPathService(db)

    def simulate(self, identity_id: str, actions: list[dict]):
        current = self.attack_service.get_attack_path(identity_id)

        if current is None:
            return None

        projected = deepcopy(current)

        risk_reduction = self._apply_actions(projected, actions)
        self._recalculate(projected, current, risk_reduction)

        return {
            "current": current,
            "projected": projected,
            "summary": {
                "current_score": current["attack_path"]["risk_score"],
                "projected_score": projected["attack_path"]["risk_score"],
                "risk_reduction": risk_reduction,
            },
        }

    def _apply_actions(self, attack_path, actions):
        total_reduction = 0

        nodes = attack_path["attack_path"]["nodes"]
        edges = attack_path["attack_path"]["edges"]
        findings = attack_path.get("findings", [])

        for action in actions:
            action_type = action.get("type")
            account_id = action.get("account_id")

            if action_type == "enable_mfa":
                reduction = self._enable_mfa(nodes, edges, findings, account_id)
                total_reduction += reduction

            elif action_type == "remove_privilege":
                reduction = self._remove_privilege(nodes, edges, account_id)
                total_reduction += reduction

        return total_reduction

    def _enable_mfa(self, nodes, edges, findings, account_id):
        reduction = 0

        for node in nodes:
            if node["type"] == "account" and node["id"] == account_id:
                details = node["details"]
                previous_risk = node["risk_contribution"]

                details["mfa_enabled"] = True

                node["risk_contribution"] = max(previous_risk - 20, 0)
                node["risk_level"] = self.attack_service._risk_level(
                    node["risk_contribution"]
                )
                node["criticality"] = min(node["risk_contribution"] * 2, 100)

                reduction = previous_risk - node["risk_contribution"]

        for edge in edges:
            if edge["target"] == account_id:
                edge["risk_contribution"] = max(
                    edge["risk_contribution"] - reduction,
                    0,
                )
                edge["risk_level"] = self.attack_service._risk_level(
                    edge["risk_contribution"]
                )

        findings[:] = [
            finding for finding in findings
            if not (
                finding.get("account_id") == account_id
                and finding.get("type") in ["weak_authentication", "policy_violation"]
            )
        ]

        return reduction

    def _remove_privilege(self, nodes, edges, account_id):
        reduction = 0

        for node in nodes:
            if node["type"] == "account" and node["id"] == account_id:
                details = node["details"]
                previous_risk = node["risk_contribution"]

                details["privilege_level"] = "Standard"

                node["risk_contribution"] = max(previous_risk - 30, 0)
                node["risk_level"] = self.attack_service._risk_level(
                    node["risk_contribution"]
                )
                node["criticality"] = min(node["risk_contribution"] * 2, 100)

                reduction = previous_risk - node["risk_contribution"]

        for edge in edges:
            if edge["target"] == account_id:
                edge["risk_contribution"] = max(
                    edge["risk_contribution"] - reduction,
                    0,
                )
                edge["risk_level"] = self.attack_service._risk_level(
                    edge["risk_contribution"]
                )

        return reduction

    def _recalculate(self, projected, current, risk_reduction):
        nodes = projected["attack_path"]["nodes"]
        edges = projected["attack_path"]["edges"]
        findings = projected.get("findings", [])
        recommendations = projected.get("recommendations", [])
        identity = projected["identity"]

        projected_score = max(
            current["attack_path"]["risk_score"] - risk_reduction,
            0,
        )

        projected["attack_path"]["risk_score"] = projected_score
        projected["attack_path"]["risk_level"] = self.attack_service._risk_level(
            projected_score
        )

        projected["summary"]["highest_risk_node"] = self.attack_service._highest_risk_node(
            nodes
        )
        projected["summary"]["top_remediation"] = self.attack_service._top_remediation(
            recommendations
        )
        projected["summary"]["blast_radius"] = self.attack_service._blast_radius(
            nodes
        )
        projected["summary"]["critical_paths"] = self.attack_service._critical_paths(
            nodes,
            edges,
        )
        projected["summary"]["ranked_paths"] = self.attack_service._ranked_paths(
            identity,
            nodes,
            edges,
            findings,
        )