from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MANIFEST = ROOT / "docs" / "release" / "RELEASE-ARTIFACT-MANIFEST.md"

SOURCE_COMMIT = (
    "e8621626a0bbe7cdc0d32e4b2d9665099000f507"
)

API_DIGEST = (
    "sha256:f611af0d0ee5e7e403008aa00d173475cb8bd8c39cca16ed6c290a428a548583"
)

WEB_DIGEST = (
    "sha256:0f04ba73554d3c9f882f017537dfd1a3f5e2a543db576d01033b15bad69b5ea4"
)

POSTGRES_DIGEST = (
    "sha256:f547ca61b8cf527287cfa87ed8f8f4bdffbe73ee34b03518eb21ed3b6e82b533"
)


def _text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def test_gate_manifest_freezes_dp2_release_version():
    text = _text()

    assert "Release Version: 0.14.0-dp2" in text
    assert "Release Stage: Design Partner Release Candidate" in text
    assert "Build Identifier: 0.14.0-dp2-e8621626" in text


def test_gate_manifest_freezes_exact_source_commit():
    text = _text()

    assert f"Source Commit: {SOURCE_COMMIT}" in text


def test_gate_manifest_freezes_exact_api_artifact():
    text = _text()

    assert "Repository: usop-core-api" in text
    assert "Tag: 0.14.0-dp2" in text
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

    assert "Backend Regression: PASS - 965 tests" in text


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


def test_gate_unfinished_release_reviews_remain_pending():
    text = _text()

    required_pending = (
        "Frontend Full Audit: PENDING",
        "Frontend Production Audit: PENDING",
        "Frontend Lint: PENDING",
        "Microsoft Entra Validation: PENDING",
        "Secret Redaction Review: PENDING",
        "Backup / Restore: PENDING",
        "Upgrade / Rollback: PENDING",
        "Clean-Room Installation: PENDING",
        "Final Decision:",
    )

    for value in required_pending:
        assert value in text
