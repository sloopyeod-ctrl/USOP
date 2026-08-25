from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
NGINX_PATH = ROOT / "frontend" / "nginx.release.conf"


def _config() -> str:
    return NGINX_PATH.read_text(encoding="utf-8")


def _exact_location_block(
    config: str,
    route: str,
) -> str:
    pattern = (
        rf"location\s*=\s*{re.escape(route)}\s*"
        r"\{(?P<body>.*?)\}"
    )

    match = re.search(
        pattern,
        config,
        flags=re.DOTALL,
    )

    assert match is not None, (
        f"Exact release nginx route {route!r} was not found."
    )

    return match.group("body")


def test_release_nginx_exposes_exact_health_route():
    block = _exact_location_block(
        _config(),
        "/health",
    )

    assert "proxy_pass http://api:8000/health;" in block


def test_release_nginx_exposes_exact_readiness_route():
    block = _exact_location_block(
        _config(),
        "/ready",
    )

    assert "proxy_pass http://api:8000/ready;" in block


def test_release_readiness_does_not_fall_through_to_spa():
    block = _exact_location_block(
        _config(),
        "/ready",
    )

    assert "try_files" not in block
    assert "index.html" not in block


def test_release_operational_routes_use_same_proxy_boundary():
    config = _config()

    health = _exact_location_block(
        config,
        "/health",
    )
    ready = _exact_location_block(
        config,
        "/ready",
    )

    required = (
        "proxy_http_version 1.1;",
        "proxy_set_header Host $host;",
        "proxy_set_header X-Forwarded-Proto $scheme;",
        (
            "proxy_set_header X-Forwarded-For "
            "$proxy_add_x_forwarded_for;"
        ),
    )

    for directive in required:
        assert directive in health
        assert directive in ready


def test_release_operational_routes_are_exact_not_prefix_routes():
    config = _config()

    assert config.count("location = /health") == 1
    assert config.count("location = /ready") == 1

    assert re.search(
        r"location\s+/health(?:\s|\{)",
        config,
    ) is None

    assert re.search(
        r"location\s+/ready(?:\s|\{)",
        config,
    ) is None
