from typing import Any

from app.domain.authorization_risk_level import AuthorizationRiskLevel


class AuthorizationEventMaterialityService:
    """
    Determine whether an authorization event requires analyst attention.

    This service consumes trusted authorization classification output. It does
    not classify roles itself and does not create reviews or decisions.
    """

    MATERIAL_RISK_LEVELS = {
        AuthorizationRiskLevel.CRITICAL.value,
        AuthorizationRiskLevel.HIGH.value,
        AuthorizationRiskLevel.MODERATE.value,
        AuthorizationRiskLevel.UNKNOWN.value,
    }

    def evaluate(
        self,
        *,
        event_type: str,
        classification: dict[str, Any],
    ) -> dict[str, Any]:
        risk_level = str(
            classification.get(
                "risk_level",
                AuthorizationRiskLevel.UNKNOWN.value,
            )
        )
        is_material = risk_level in self.MATERIAL_RISK_LEVELS
        reasons = list(classification.get("reasons", []))

        if risk_level == AuthorizationRiskLevel.UNKNOWN.value:
            reasons.append(
                "Authorization evidence is incomplete; analyst review is "
                "required rather than silently accepting uncertainty."
            )

        if event_type == "ROLE_UPDATED":
            reasons.append(
                "A persisted authorization relationship changed."
            )
        elif event_type == "ROLE_ASSIGNED":
            reasons.append(
                "A new authorization relationship was established."
            )

        return {
            "risk_level": risk_level,
            "is_material": is_material,
            "materiality_source": "AuthorizationRiskPolicy",
            "reasons": reasons,
            "classification": classification,
        }
