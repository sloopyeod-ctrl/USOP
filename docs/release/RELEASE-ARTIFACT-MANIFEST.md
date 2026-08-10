# USOP Release Artifact Manifest

## Purpose

This manifest records the immutable identity and validation evidence for a frozen USOP release.

Do not treat validation-build identifiers as final release identifiers.

## Release Identity

```text
Product: USOP Core
Release Version: PENDING
Release Stage: Release Candidate
Release Date: PENDING
Source Commit: PENDING
Build Identifier: PENDING
```

## Release Images

### API

```text
Repository: PENDING
Tag: PENDING
Digest: PENDING
Base: python:3.12-alpine
Runtime User: usop
Critical: PENDING
High: PENDING
SBOM: PENDING
Provenance: PENDING
```

### Web

```text
Repository: PENDING
Tag: PENDING
Digest: PENDING
Base: nginx:1-alpine-slim
Critical: PENDING
High: PENDING
SBOM: PENDING
Provenance: PENDING
```

### PostgreSQL

```text
Repository: postgres
Tag: 17-alpine
Digest: PENDING
Critical: PENDING
High: PENDING
Exception Reference: EX-001 if still applicable
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
Backend Regression:
Frontend Full Audit:
Frontend Production Audit:
Frontend Lint:
Frontend Build:
API Critical/High Scan:
Web Critical/High Scan:
PostgreSQL Scan:
Vulnerability Exception Review:
Runtime User Check:
Runtime Immutability Check:
Health Check:
Web Check:
Microsoft Entra Validation:
Secret Redaction Review:
Backup / Restore:
Upgrade / Rollback:
Clean-Room Installation:
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
Manifest Reviewed By:
Security Review:
Release Engineering Review:
Documentation Review:
Clean-Room Review:
Freeze Date:
Final Decision:
```

## Integrity Principle

The release artifact, documentation, image digests, scan evidence, and manifest must describe the same frozen build.
