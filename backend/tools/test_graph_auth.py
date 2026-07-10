import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"

# Allow imports from backend/app when run from the repository root.
sys.path.insert(0, str(BACKEND_ROOT))

from app.security.auth.MicrosoftGraphAuthService import (
    MicrosoftGraphAuthService,
)


def main() -> int:
    if not ENV_FILE.exists():
        print(f"[FAILED] Environment file not found: {ENV_FILE}")
        return 1

    load_dotenv(dotenv_path=ENV_FILE, override=False)

    print("USOP Microsoft Graph Authentication Test")
    print("----------------------------------------")
    print(f"Environment file: {ENV_FILE}")
    print("Secret provider: environment")
    print("Requesting app-only Microsoft Graph token...")

    try:
        auth_service = MicrosoftGraphAuthService()
        token = auth_service.get_token()
    except Exception as exc:
        print()
        print("[FAILED] Microsoft Graph authentication failed.")
        print(f"Reason: {exc}")
        return 1

    print()
    print("[SUCCESS] Microsoft Graph authentication succeeded.")
    print(f"Token type: {token.token_type}")
    print(f"Expires at: {token.expires_at.isoformat()}")
    print(f"Expired: {token.is_expired()}")
    print("Access token acquired but intentionally not displayed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())