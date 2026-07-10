import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

# Allow imports from backend/app when run from the repository root.
sys.path.insert(0, str(BACKEND_ROOT))

from app.security.graph.GraphClient import GraphClient

def mask_user_principal_name(value: str | None) -> str:
    if not value or "@" not in value:
        return "Unavailable"

    local_part, domain = value.split("@", 1)

    if len(local_part) <= 2:
        masked_local = local_part[0] + "*"
    else:
        masked_local = f"{local_part[:2]}{'*' * max(len(local_part) - 2, 3)}"

    return f"{masked_local}@{domain}"


def format_user(user: dict[str, Any]) -> str:
    display_name = user.get("displayName") or "Unknown"
    user_principal_name = mask_user_principal_name(
    user.get("userPrincipalName")
    )
    account_enabled = user.get("accountEnabled")

    return (
        f"Name: {display_name}\n"
        f"User principal name: {user_principal_name}\n"
        f"Account enabled: {account_enabled}"
    )


def main() -> int:
    if not ENV_FILE.exists():
        print(f"[FAILED] Environment file not found: {ENV_FILE}")
        return 1

    load_dotenv(dotenv_path=ENV_FILE, override=False)

    print("USOP Microsoft Graph User Collection Test")
    print("-----------------------------------------")
    print("Requesting up to five users from Microsoft Graph...")

    try:
        graph_client = GraphClient()

        response = graph_client.get(
            "/users",
            params={
                "$top": 5,
                "$select": (
                    "id,"
                    "displayName,"
                    "userPrincipalName,"
                    "accountEnabled"
                ),
            },
        )
    except Exception as exc:
        print()
        print("[FAILED] Microsoft Graph user collection failed.")
        print(f"Reason: {exc}")
        return 1

    users = response.get("value", [])

    if not isinstance(users, list):
        print()
        print("[FAILED] Microsoft Graph returned an invalid users collection.")
        return 1

    print()
    print("[SUCCESS] Microsoft Graph user collection succeeded.")
    print(f"Users returned: {len(users)}")

    if not users:
        print("No users were returned by the tenant.")
        return 0

    print()

    for index, user in enumerate(users, start=1):
        print(f"User {index}")
        print(format_user(user))
        print("-" * 40)

    if response.get("@odata.nextLink"):
        print("Additional users are available through Microsoft Graph paging.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())