from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

COMPOSE = ROOT / "docker-compose.release.yml"
WEB_DOCKERFILE = ROOT / "frontend" / "Dockerfile.release"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_web_runtime_declares_non_root_user():
    text = _text(WEB_DOCKERFILE)

    assert "USER nginx" in text


def test_gate_web_service_runs_as_nginx():
    text = _text(COMPOSE)

    assert "    user: nginx" in text


def test_gate_web_service_drops_all_capabilities():
    text = _text(COMPOSE)

    assert "    cap_drop:" in text
    assert "      - ALL" in text


def test_gate_web_service_disables_privilege_escalation():
    text = _text(COMPOSE)

    assert "    security_opt:" in text
    assert "      - no-new-privileges:true" in text


def test_gate_web_runtime_has_only_required_tmpfs_paths():
    text = _text(COMPOSE)

    assert "/run:rw,uid=101,gid=101,mode=755" in text
    assert "/var/cache/nginx:rw,uid=101,gid=101,mode=755" in text


def test_gate_web_still_uses_unprivileged_application_port():
    dockerfile = _text(WEB_DOCKERFILE)
    compose = _text(COMPOSE)

    assert "EXPOSE 8080" in dockerfile
    assert '"${USOP_WEB_PORT:-8080}:8080"' in compose

def test_gate_api_runtime_declares_non_root_user():
    text = _text(ROOT / "backend" / "Dockerfile.release")

    assert "USER usop" in text


def test_gate_api_service_drops_all_capabilities():
    text = _text(COMPOSE)

    api_start = text.index("  api:")
    web_start = text.index("  web:")
    api = text[api_start:web_start]

    assert "    cap_drop:" in api
    assert "      - ALL" in api


def test_gate_api_service_disables_privilege_escalation():
    text = _text(COMPOSE)

    api_start = text.index("  api:")
    web_start = text.index("  web:")
    api = text[api_start:web_start]

    assert "    security_opt:" in api
    assert "      - no-new-privileges:true" in api


def test_gate_api_does_not_require_privileged_mode():
    text = _text(COMPOSE)

    api_start = text.index("  api:")
    web_start = text.index("  web:")
    api = text[api_start:web_start]

    assert "privileged: true" not in api


def test_gate_api_remains_internal_only():
    text = _text(COMPOSE)

    api_start = text.index("  api:")
    web_start = text.index("  web:")
    api = text[api_start:web_start]

    assert "ports:" not in api
    assert "8000:8000" not in api

def test_gate_api_root_filesystem_is_read_only():
    text = _text(COMPOSE)

    api_start = text.index("  api:")
    web_start = text.index("  web:")
    api = text[api_start:web_start]

    assert "    read_only: true" in api


def test_gate_web_root_filesystem_is_read_only():
    text = _text(COMPOSE)

    web_start = text.index("  web:")
    web = text[web_start:]

    assert "    read_only: true" in web


def test_gate_api_has_only_controlled_transient_tmpfs():
    text = _text(COMPOSE)

    api_start = text.index("  api:")
    web_start = text.index("  web:")
    api = text[api_start:web_start]

    assert "    tmpfs:" in api
    assert (
        "      - /tmp:rw,nosuid,nodev,noexec,mode=1777"
        in api
    )


def test_gate_postgres_is_not_falsely_declared_immutable():
    text = _text(COMPOSE)

    postgres_start = text.index("  postgres:")
    migrate_start = text.index("  migrate:")
    postgres = text[postgres_start:migrate_start]

    assert "    read_only: true" not in postgres