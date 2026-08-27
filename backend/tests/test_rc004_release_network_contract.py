from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

COMPOSE = ROOT / "docker-compose.release.yml"
NGINX = ROOT / "frontend" / "nginx.release.conf"

SECURITY_GUIDE = (
    ROOT / "docs" / "customer" / "03-Security-Deployment-Guide.md"
)
INSTALL_GUIDE = (
    ROOT / "docs" / "customer" / "01-Installation-Guide.md"
)
KNOWN_LIMITATIONS = (
    ROOT / "docs" / "customer" / "08-Known-Limitations.md"
)
RELEASE_NOTES = (
    ROOT / "docs" / "customer" / "07-Release-Notes.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_release_publishes_only_web_host_port():
    text = _text(COMPOSE)

    assert '"${USOP_WEB_PORT:-8080}:8080"' in text
    assert "8000:8000" not in text
    assert "5432:5432" not in text


def test_gate_api_and_database_are_documented_internal_only():
    text = _text(SECURITY_GUIDE)

    assert "API TCP 8000" in text
    assert "PostgreSQL TCP 5432" in text
    assert "Docker-internal only" in text


def test_gate_runtime_egress_is_narrowly_documented():
    text = _text(SECURITY_GUIDE)

    assert "login.microsoftonline.com" in text
    assert "graph.microsoft.com" in text
    assert "TCP 443" in text
    assert "Broad unrestricted Internet egress is not" in text


def test_gate_dns_requirement_is_explicit():
    text = _text(SECURITY_GUIDE)

    assert "### DNS" in text
    assert "login.microsoftonline.com" in text
    assert "graph.microsoft.com" in text


def test_gate_bundled_ingress_remains_http_8080():
    nginx = _text(NGINX)
    guide = _text(SECURITY_GUIDE)

    assert "listen 8080;" in nginx
    assert "bundled USOP web container listens on HTTP TCP 8080" in guide

def test_gate_network_accessible_deployment_requires_tls_boundary():
    text = _text(SECURITY_GUIDE)

    assert "TLS termination is required ahead of USOP" in text
    assert "customer-controlled" in text


def test_gate_internal_services_are_not_customer_ingress():
    text = _text(SECURITY_GUIDE)

    assert (
        "must not expose Docker-internal API TCP 8000 or PostgreSQL TCP 5432"
        in text
    )


def test_gate_proxy_support_is_not_overclaimed():
    security = _text(SECURITY_GUIDE)
    limitations = _text(KNOWN_LIMITATIONS)

    assert (
        "Explicit customer HTTP or HTTPS proxy configuration has not been validated"
        in security
    )
    assert (
        "Explicit HTTP/HTTPS proxy configuration has not been validated"
        in limitations
    )


def test_gate_ipv6_only_egress_is_not_overclaimed():
    security = _text(SECURITY_GUIDE)
    limitations = _text(KNOWN_LIMITATIONS)

    assert "IPv6-only Docker egress has not been validated" in security
    assert "IPv6-only Docker egress has not been validated" in limitations


def test_gate_customer_docs_publish_same_runtime_boundary():
    install = _text(INSTALL_GUIDE)
    release = _text(RELEASE_NOTES)

    for required in (
        "login.microsoftonline.com",
        "graph.microsoft.com",
        "TCP 8080",
        "TCP 8000",
        "TCP 5432",
    ):
        assert required in install
        assert required in release