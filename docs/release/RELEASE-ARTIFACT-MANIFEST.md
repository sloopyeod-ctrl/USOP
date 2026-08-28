# USOP Release Artifact Manifest

## Purpose

This manifest records the immutable identity and validation evidence for a frozen USOP release.

Do not treat validation-build identifiers as final release identifiers.

## Release Identity

```text
Product: USOP Core
Release Version: 0.14.0-dp2
Release Stage: Design Partner Release Candidate
Release Date: 2026-08-27
Source Commit: e8621626a0bbe7cdc0d32e4b2d9665099000f507
Build Identifier: 0.14.0-dp2-e8621626
```

## Release Images

### API

```text
Repository: usop-core-api
Tag: 0.14.0-dp2
Digest: sha256:f611af0d0ee5e7e403008aa00d173475cb8bd8c39cca16ed6c290a428a548583
Base: python:3.12-alpine@sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31
Runtime User: usop
Critical: 0
High: 0
SBOM: Generated during frozen BuildKit manufacturing
Provenance: mode=max; source revision e8621626a0bbe7cdc0d32e4b2d9665099000f507
```

### Web

```text
Repository: usop-core-web
Tag: 0.14.0-dp2
Digest: sha256:0f04ba73554d3c9f882f017537dfd1a3f5e2a543db576d01033b15bad69b5ea4
Base: nginx:1-alpine-slim@sha256:1870de6d59aafee152589b64404556d2535922cdd998e6dac1c4888c938ed8f9
Runtime User: nginx
Critical: 0
High: 0
SBOM: Generated during frozen BuildKit manufacturing
Provenance: mode=max; source revision e8621626a0bbe7cdc0d32e4b2d9665099000f507
```

### PostgreSQL

```text
Repository: usop-core-postgres
Tag: 0.14.0-dp2
Digest: sha256:f547ca61b8cf527287cfa87ed8f8f4bdffbe73ee34b03518eb21ed3b6e82b533
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

## Current RC Validation Evidence

The following identifiers are validation evidence only and must not be presented as final frozen release digests:

```text
API validation digest:
sha256:ed8976157bdca8533fa96eb16e2406e4875e4fd25a20f120282d1064b6e4ec37

WEB validation digest:
sha256:a2f897999ea38b81d5b0a502d923a89049d5062d85358dcda5c76f08305da2de

POSTGRES validation digest:
sha256:742f40ea20b9ff2ff31db5458d127452988a2164df9e17441e191f3b72252193
```

These values must be replaced or explicitly reconfirmed during final freeze.

## Dependency Evidence

```text
Backend runtime lock: backend/requirements.lock
Backend dev/test lock: backend/requirements-dev.lock
Frontend manifest: frontend/package.json
Frontend lock: frontend/package-lock.json
```

## Validation Evidence

```text
Backend Regression: PASS - 965 tests
Frontend Full Audit: PENDING
Frontend Production Audit: PENDING
Frontend Lint: PENDING
Frontend Build: PASS - final DP2 web artifact manufactured successfully
API Critical/High Scan: PASS - 0 Critical / 0 High
Web Critical/High Scan: PASS - 0 Critical / 0 High
PostgreSQL Scan: PASS - USOP-introduced 0 Critical / 0 High; raw inherited 2 Critical / 20 High
Vulnerability Exception Review: PENDING
Runtime User Check: PASS
Runtime Immutability Check: PENDING
Health Check: PASS - /health HTTP 200
Web Check: PASS - / HTTP 200
Microsoft Entra Validation: PENDING
Secret Redaction Review: PENDING
Backup / Restore: PENDING
Upgrade / Rollback: PENDING
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
