from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MANIFEST = ROOT / "docs" / "release" / "RELEASE-ARTIFACT-MANIFEST.md"

SOURCE_COMMIT = (
    "7c74f7e3e44b91cfe5f20a77b9b4ca5aed40810f"
)

API_DIGEST = (
    "sha256:39d6a4c4f8617f5be37bfcaccedbd2851b4fa335ea5b4ccb6981b98ec96e796a"
)

WEB_DIGEST = (
    "sha256:7ce6a57ded6a6f95da35594b2ee8d8a7aa11b1355a858a18c0891c49c5e4a3b5"
)

POSTGRES_DIGEST = (
    "sha256:a939c8d864fddfb03e36e16a9188c73e0cf052ed3a17ba290bd4a8f09b8135cd"
)


def _text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def test_gate_manifest_freezes_dp2_release_version():
    text = _text()

    assert "Release Version: 0.14.0-dp2-final" in text
    assert "Release Stage: Design Partner Release Candidate" in text
    assert "Build Identifier: 0.14.0-dp2-final-7c74f7e" in text


def test_gate_manifest_freezes_exact_source_commit():
    text = _text()

    assert f"Source Commit: {SOURCE_COMMIT}" in text


def test_gate_manifest_freezes_exact_api_artifact():
    text = _text()

    assert "Repository: usop-core-api" in text
    assert "Tag: 0.14.0-dp2-final" in text
    assert f"Digest: {API_DIGEST}" in text


def test_gate_manifest_freezes_exact_web_artifact():
    text = _text()

    assert "Repository: usop-core-web" in text
    assert f"Digest: {WEB_DIGEST}" in text


def test_gate_manifest_freezes_exact_postgres_artifact():
    text = _text()

    assert "Repository: usop-core-postgres" in text
    assert f"Digest: {POSTGRES_DIGEST}" in text


def test_gate_manifest_records_clean_api_and_web_scans():
    text = _text()

    assert "API Critical/High Scan: PASS - 0 Critical / 0 High" in text
    assert "Web Critical/High Scan: PASS - 0 Critical / 0 High" in text


def test_gate_manifest_preserves_postgres_inherited_finding_boundary():
    text = _text()

    assert "USOP-Introduced Critical: 0" in text
    assert "USOP-Introduced High: 0" in text
    assert "Raw Inherited Critical: 2" in text
    assert "Raw Inherited High: 20" in text
    assert "/usr/local/bin/gosu removed from final USOP runtime filesystem" in text


def test_gate_manifest_records_authoritative_backend_regression():
    text = _text()

    assert "Backend Regression: PASS - 987 tests" in text


def test_gate_artifact_identity_placeholders_are_eliminated():
    text = _text()

    forbidden = (
        "Release Version: PENDING",
        "Source Commit: PENDING",
        "Build Identifier: PENDING",
        "Digest: PENDING",
    )

    for value in forbidden:
        assert value not in text


def test_gate_completed_release_reviews_are_recorded():
    text = _text()

    required_completed = (
        "Clean-Room Installation: PASS",
        "Manifest Reviewed By: USOP Release Review",
        "Security Review: PASS",
        "Release Engineering Review: PASS",
        "Documentation Review: PASS",
        "Clean-Room Review: PASS",
    )

    for value in required_completed:
        assert value in text

    required_final = (
        "Freeze Date: 2026-08-28",
        "Final Decision: APPROVED FOR DESIGN PARTNER DISTRIBUTION",
    )

    for value in required_final:
        assert value in text
