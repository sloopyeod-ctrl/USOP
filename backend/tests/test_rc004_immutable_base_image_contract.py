from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

BACKEND = ROOT / "backend" / "Dockerfile.release"
FRONTEND = ROOT / "frontend" / "Dockerfile.release"
COMPOSE = ROOT / "docker-compose.release.yml"

PYTHON_DIGEST = (
    "sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31"
)
NODE_DIGEST = (
    "sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32"
)
NGINX_DIGEST = (
    "sha256:1870de6d59aafee152589b64404556d2535922cdd998e6dac1c4888c938ed8f9"
)
POSTGRES_DIGEST = (
    "sha256:18cfe3ef5e6815560c98237d6216d1e5119702fb0f3894c8785dd58b8bbe5d73"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_backend_builder_uses_frozen_python_base():
    text = _text(BACKEND)

    expected = f"FROM python:3.12-alpine@{PYTHON_DIGEST} AS builder"
    assert expected in text


def test_gate_backend_runtime_uses_same_frozen_python_base():
    text = _text(BACKEND)

    expected = f"FROM python:3.12-alpine@{PYTHON_DIGEST} AS runtime"
    assert expected in text


def test_gate_frontend_builder_uses_frozen_node_base():
    text = _text(FRONTEND)

    expected = f"FROM node:22-alpine@{NODE_DIGEST} AS build"
    assert expected in text


def test_gate_frontend_runtime_uses_frozen_nginx_base():
    text = _text(FRONTEND)

    expected = f"FROM nginx:1-alpine-slim@{NGINX_DIGEST}"
    assert expected in text


def test_gate_postgres_uses_frozen_official_image():
    text = _text(COMPOSE)

    expected = f"image: postgres:17-alpine@{POSTGRES_DIGEST}"
    assert expected in text


def test_gate_every_release_from_instruction_is_digest_pinned():
    lines = (
        _text(BACKEND).splitlines()
        + _text(FRONTEND).splitlines()
    )

    release_from_lines = [
        line.strip()
        for line in lines
        if line.strip().startswith("FROM ")
    ]

    assert release_from_lines

    for line in release_from_lines:
        assert "@sha256:" in line


def test_gate_postgres_release_reference_is_not_tag_only():
    text = _text(COMPOSE)

    assert "image: postgres:17-alpine@" in text
    assert (
        "image: postgres:17-alpine\n"
        not in text
    )