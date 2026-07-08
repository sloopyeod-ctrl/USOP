class ExposureScoreEngine:
    """
    Calculates an overall identity exposure score.

    The score is derived from multiple security dimensions.
    """

    def calculate(self, graph: dict, identity_risk: dict):

        breakdown = {
            "authentication": 0,
            "privileged_access": 0,
            "policy": 0,
            "dormant_accounts": 0,
            "attack_surface": 0,
        }

        #
        # Authentication
        #

        for account in graph["accounts"]:

            if not account.get("mfa_enabled", False):
                breakdown["authentication"] += 10

        #
        # Privileged Accounts
        #

        for account in graph["accounts"]:

            if account.get("privilege_level") == "Privileged":
                breakdown["privileged_access"] += 15

        #
        # Policy Violations
        #

        if identity_risk:

            for finding in identity_risk["findings"]:

                if finding["type"] == "policy_violation":
                    breakdown["policy"] += 20

                if finding["type"] == "dormant_account":
                    breakdown["dormant_accounts"] += 5

        #
        # Attack Surface
        #

        breakdown["attack_surface"] = (
            len(graph["accounts"]) * 2
            + len(graph["groups"]) * 3
            + len(graph["roles"]) * 4
        )

        total = sum(breakdown.values())

        total = min(total, 100)

        if total >= 90:
            rating = "Critical"

        elif total >= 70:
            rating = "High"

        elif total >= 40:
            rating = "Medium"

        else:
            rating = "Low"

        return {
            "score": total,
            "rating": rating,
            "breakdown": breakdown,
        }