# USOP Release Artifact Manifest

## Purpose

This manifest records the immutable identity and validation evidence for a frozen USOP release.

Do not treat validation-build identifiers as final release identifiers.

## Release Identity

```text
Product: USOP Core
Release Version: 0.14.0-dp2-final
Release Stage: Design Partner Release Candidate
Release Date: 2026-08-27
Source Commit: 7c74f7e3e44b91cfe5f20a77b9b4ca5aed40810f
Build Identifier: 0.14.0-dp2-final-7c74f7e
```

## Release Images

### API

```text
Repository: usop-core-api
Tag: 0.14.0-dp2-final
Digest: sha256:39d6a4c4f8617f5be37bfcaccedbd2851b4fa335ea5b4ccb6981b98ec96e796a
Base: python:3.12-alpine@sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31
Runtime User: usop
Critical: 0
High: 0
SBOM: Generated during frozen BuildKit manufacturing
Provenance: mode=max; source revision 7c74f7e3e44b91cfe5f20a77b9b4ca5aed40810f
```

### Web

```text
Repository: usop-core-web
Tag: 0.14.0-dp2-final
Digest: sha256:7ce6a57ded6a6f95da35594b2ee8d8a7aa11b1355a858a18c0891c49c5e4a3b5
Base: nginx:1-alpine-slim@sha256:1870de6d59aafee152589b64404556d2535922cdd998e6dac1c4888c938ed8f9
Runtime User: nginx
Critical: 0
High: 0
SBOM: Generated during frozen BuildKit manufacturing
Provenance: mode=max; source revision 7c74f7e3e44b91cfe5f20a77b9b4ca5aed40810f
```

### PostgreSQL

```text
Repository: usop-core-postgres
Tag: 0.14.0-dp2-final
Digest: sha256:a939c8d864fddfb03e36e16a9188c73e0cf052ed3a17ba290bd4a8f09b8135cd
Base: postgres:17-alpine@sha256:18cfe3ef5e6815560c98237d6216d1e5119702fb0f3894c8785dd58b8bbe5d73
Runtime User: postgres
USOP-Introduced Critical: 0
USOP-Introduced High: 0
Raw Inherited Critical: 2
Raw Inherited High: 20
Inherited Finding: Go stdlib 1.24.6 attributed to /usr/local/bin/gosu in the upstream base
Runtime Disposition: /usr/local/bin/gosu removed from final USOP runtime filesystem
OpenSSL Runtime: libssl3=3.5.8-r0; libcrypto3=3.5.8-r0
Exception Reference: inherited/deleted-component adjudication evidence retained
```

## Dependency Evidence

```text
Backend runtime lock: backend/requirements.lock
Backend dev/test lock: backend/requirements-dev.lock
Frontend manifest: frontend/package.json
Frontend lock: frontend/package-lock.json
```

## Validation Evidence

```text
Backend Regression: PASS - 987 tests
Frontend Full Audit: PASS - 0 vulnerabilities
Frontend Production Audit: PASS - 0 vulnerabilities
Frontend Lint: PASS
Frontend Build: PASS - final DP2 web artifact manufactured successfully
API Critical/High Scan: PASS - 0 Critical / 0 High
Web Critical/High Scan: PASS - 0 Critical / 0 High
PostgreSQL Scan: PASS - USOP-introduced 0 Critical / 0 High; raw inherited 2 Critical / 20 High
Vulnerability Exception Review: PASS - inherited PostgreSQL base findings documented; USOP-introduced 0 Critical / 0 High
Runtime User Check: PASS
Runtime Immutability Check: PASS - API and Web read-only root filesystems with controlled tmpfs
Health Check: PASS - /health HTTP 200
Web Check: PASS - / HTTP 200
Microsoft Entra Validation: PASS - live two-pass synchronization; 5 identities / 5 accounts / 6 groups / 14 memberships / 15 roles / 15 role assignments; 0 duplicate provider identifiers
Secret Redaction Review: PASS - secret non-disclosure contract passed
Backup / Restore: PASS - logical backup restored in isolated PostgreSQL environment with schema and recovery canary verified
Upgrade / Rollback: PASS - downgrade one revision and re-upgrade to head with data preserved
Clean-Room Installation: PENDING
```

## Customer Documentation

Required RC1 customer documents:

```text
01-Installation-Guide.md
02-Secrets-Configuration-Guide.md
03-Security-Deployment-Guide.md
04-User-Guide.md
05-Design-Partner-Guide.md
06-Feedback-Questionnaire.md
07-Release-Notes.md
08-Known-Limitations.md
```

## Freeze Confirmation

```text
Manifest Reviewed By: PENDING
Security Review: PENDING
Release Engineering Review: PENDING
Documentation Review: PENDING
Clean-Room Review: PENDING
Freeze Date: PENDING
Final Decision: PENDING
```

## Integrity Principle

The release artifact, documentation, image digests, scan evidence, and manifest must describe the same frozen build.
