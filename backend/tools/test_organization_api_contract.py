import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from fastapi.testclient import TestClient

from app.main import app


EXPECTED_OPERATIONS = {
    (
        "/api/v1/organizations/",
        "get",
    ),
    (
        "/api/v1/organizations/",
        "post",
    ),
    (
        "/api/v1/organizations/slug/{slug}",
        "get",
    ),
    (
        "/api/v1/organizations/{organization_id}",
        "get",
    ),
}


def collect_openapi_operations() -> set[tuple[str, str]]:
    schema = app.openapi()
    paths = schema.get("paths", {})

    supported_methods = {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "options",
        "head",
    }

    return {
        (
            path,
            method.lower(),
        )
        for path, operations in paths.items()
        for method in operations
        if method.lower() in supported_methods
    }


def main() -> int:
    print("USOP Organization API Contract Regression")
    print("-----------------------------------------")

    errors: list[str] = []

    actual_operations = collect_openapi_operations()

    missing_operations = (
        EXPECTED_OPERATIONS
        - actual_operations
    )

    print("OpenAPI Organization operations:")

    for path, method in sorted(
        operation
        for operation in actual_operations
        if operation[0].startswith(
            "/api/v1/organizations"
        )
    ):
        print(f"- {method.upper()} {path}")

    if missing_operations:
        for path, method in sorted(
            missing_operations
        ):
            errors.append(
                "Missing OpenAPI operation: "
                f"{method.upper()} {path}"
            )

    # FastAPI 0.138.x uses lazy nested-router composition. The
    # authoritative frontend contract is therefore validated through
    # OpenAPI and actual request dispatch instead of iterating app.routes.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=(
                "Using `httpx` with "
                "`starlette.testclient` is deprecated"
            ),
        )

        client = TestClient(
            app,
            raise_server_exceptions=True,
        )

        openapi_response = client.get(
            "/openapi.json"
        )

        missing_id_response = client.get(
            "/api/v1/organizations/"
            "00000000-0000-0000-0000-000000000000"
        )

        missing_slug_response = client.get(
            "/api/v1/organizations/slug/"
            "organization-that-does-not-exist"
        )

    if openapi_response.status_code != 200:
        errors.append(
            "OpenAPI endpoint did not return HTTP 200."
        )

    endpoint_responses = (
        (
            "Organization ID endpoint",
            missing_id_response,
        ),
        (
            "Organization slug endpoint",
            missing_slug_response,
        ),
    )

    for name, response in endpoint_responses:
        if response.status_code != 404:
            errors.append(
                f"{name} returned HTTP "
                f"{response.status_code}; expected 404."
            )
            continue

        payload = response.json()

        if (
            payload.get("detail")
            != "Organization not found."
        ):
            errors.append(
                f"{name} did not return the "
                "Organization domain-specific 404."
            )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print()
    print("Runtime routing:")
    print(
        "- GET /openapi.json -> "
        f"{openapi_response.status_code}"
    )
    print(
        "- GET missing Organization ID -> "
        f"{missing_id_response.status_code}"
    )
    print(
        "- GET missing Organization slug -> "
        f"{missing_slug_response.status_code}"
    )

    print()
    print("Validation: PASSED")
    print(
        "The Organization API is exposed through "
        "OpenAPI and dispatches requests to the "
        "expected backend handlers under FastAPI's "
        "lazy router-composition model."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
