RISK_WEIGHTS = {
    "privileged_role": 40,
    "privileged_group": 25,
    "mfa_disabled": 30,
    "weak_authentication": 20,
    "unknown_authentication_provider": 10,
    "unknown_authentication_strength": 10,
    "dormant_account": 15,
    "orphaned_account": 35,
}


def risk_level(score: int) -> str:
    if score >= 75:
        return "Critical"

    if score >= 50:
        return "High"

    if score >= 25:
        return "Moderate"

    return "Low"