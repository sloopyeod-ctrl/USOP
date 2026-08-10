# USOP Release Validation Procedure

## Purpose

This procedure defines the ordered validation sequence required before a USOP release candidate may be frozen for Design Partner or production distribution.

## Principle

Validation is performed against the exact release configuration.

Do not substitute development containers, developer workstation state, cached test data, or undocumented configuration for the release artifact.

## Phase 1 — Repository Baseline

Confirm:

```powershell
git status
git log -1 --oneline
git diff --check
```

Requirements:

- intended source commit identified;
- no unexpected source modifications;
- no production secrets present;
- dependency lockfiles present;
- release Dockerfiles present;
- release Compose file present.

## Phase 2 — Backend Validation

Run the complete supported backend regression suite.

Minimum gate:

```text
Regression: PASS
Dependency integrity: PASS
```

Record:

- Python version;
- number of passing tests;
- warnings requiring future migration;
- failed/skipped tests, if any;
- release-blocking defects.

## Phase 3 — Frontend Validation

Run:

```powershell
npm audit
npm audit --omit=dev
npm run lint
npm run build
```

Minimum gate:

```text
Full audit: 0 unresolved release-blocking vulnerabilities
Production audit: 0 unresolved release-blocking vulnerabilities
Lint: PASS
Build: PASS
```

Track bundle-size or optimization warnings separately unless they are determined to create material impact.

## Phase 4 — Attested Container Build

Build from the release Dockerfiles and release Compose definition.

Required build properties:

- fresh base-image pull;
- no development bind mounts;
- SBOM generation;
- provenance generation;
- no production secrets in build context.

Example build intent:

```text
docker compose build --pull --no-cache --sbom=true --provenance=mode=max
```

Exact command syntax may vary with the supported Docker/Compose version and must be frozen in the installation procedure.

## Phase 5 — Runtime Validation

Start the isolated release stack.

Verify:

- PostgreSQL health;
- API health;
- web health;
- approved host port exposure;
- API internal-only exposure;
- PostgreSQL internal-only exposure;
- API runtime user;
- API package-install tooling absence;
- no development source mounts.

Minimum application gate:

```text
/health: PASS
Web root: HTTP 200
React application shell: PASS
```

## Phase 6 — Vulnerability Validation

Scan the exact built images.

Required:

### USOP API

- no unresolved Critical vulnerability under USOP control;
- no unresolved High vulnerability under USOP control;
- non-root runtime;
- minimal runtime content.

### USOP Web

- no unresolved Critical vulnerability under USOP control;
- no unresolved High vulnerability under USOP control;
- minimal runtime content.

### PostgreSQL

- scan the exact official image;
- record current Critical/High counts;
- update the Vulnerability Exception Register when upstream findings remain;
- verify no supported fixed official artifact has been ignored.

## Phase 7 — Supply-Chain Evidence

Capture:

- SBOM;
- provenance;
- image digest;
- base-image identifier;
- source commit;
- release version.

If local tooling cannot independently verify generated attestations, the supply-chain gate remains open until verification succeeds in the final publication workflow.

## Phase 8 — Microsoft Entra Validation

Before RC1 freeze, validate the exact supported connector contract:

- tenant authentication;
- client credentials;
- minimum Graph permissions;
- supported user collection;
- supported group collection;
- supported role collection;
- pagination behavior;
- material authorization-delta behavior;
- documented PIM limitations.

No permission should be requested solely because it was convenient during development.

## Phase 9 — Security Configuration Validation

Confirm:

- `.env` contract matches runtime behavior;
- RC secret-provider support is documented accurately;
- no secret appears in logs;
- database secrets are customer-controlled;
- network ports are documented;
- outbound destinations are documented;
- TLS responsibility is documented.

## Phase 10 — Persistence and Recovery Validation

Before freeze, validate:

- persistent volume behavior;
- backup procedure;
- restore procedure;
- migration behavior;
- supported upgrade path;
- supported rollback path.

## Phase 11 — Clean-Room Installation

Install USOP on a clean host using only:

- frozen release package;
- frozen customer documentation;
- documented prerequisites;
- customer-generated secrets.

The clean-room installer must not require:

- developer workstation state;
- source-tree secrets;
- VS Code;
- unpublished environment variables;
- prior local database contents;
- undocumented commands;
- developer coaching.

Any undocumented dependency discovered here blocks freeze.

## Phase 12 — Release Freeze

Complete the Release Artifact Manifest.

Confirm:

- final source commit;
- final release version;
- final image digests;
- final scan result;
- final exception status;
- final documentation set;
- clean-room result.

After freeze, any deployment-critical change reopens validation.

## Final Release Decision

```text
Backend Regression: PASS / FAIL
Frontend Audit: PASS / FAIL
Frontend Lint: PASS / FAIL
Frontend Build: PASS / FAIL
API Scan: PASS / FAIL
Web Scan: PASS / FAIL
Postgres Exception Review: PASS / FAIL
SBOM: PASS / FAIL
Provenance: PASS / FAIL
Entra Contract: PASS / FAIL
Secrets Contract: PASS / FAIL
Backup / Restore: PASS / FAIL
Upgrade / Rollback: PASS / FAIL
Clean-Room Install: PASS / FAIL
Documentation Reconciliation: PASS / FAIL

Release Decision: APPROVED / NOT APPROVED
```
