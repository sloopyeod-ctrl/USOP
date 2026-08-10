# USOP Release Security Standard

## Purpose

This document defines the minimum release-security requirements for USOP Core release candidates and production releases.

The standard exists to ensure that the exact artifact delivered to a customer is the exact artifact that was dependency-reviewed, regression-tested, container-scanned, deployment-validated, and frozen.

A release is not approved because development is complete.

A release is approved only when all applicable release gates are satisfied or an explicit, documented upstream exception has been accepted.

## Scope

This standard applies to:

- USOP application source code;
- Python runtime dependencies;
- frontend runtime and build dependencies;
- container base images;
- Docker Compose release configuration;
- customer-facing environment configuration;
- customer release documentation;
- release manifests;
- SBOM and provenance evidence;
- vulnerability exceptions;
- patch and rebuild activity;
- final release packaging.

## Release Security Principles

### Exact Artifact Validation

The artifact delivered to a customer must be the same artifact that passed final validation.

Any post-validation change to application code, dependency versions, container images, runtime configuration, deployment configuration, environment-variable contract, or deployment-critical documentation reopens the relevant validation gates.

### Fix What USOP Controls

Known fixable Critical or High vulnerabilities in USOP-controlled application or runtime images are release blockers.

USOP must not intentionally ship a known fixable Critical or High vulnerability in a component under direct USOP release-engineering control.

### Document What USOP Cannot Control

An unresolved vulnerability in an upstream official image is not silently ignored.

It must be:

1. verified against the exact candidate image;
2. recorded in the Vulnerability Exception Register;
3. evaluated for exploitability and operational relevance;
4. associated with a current upstream remediation status;
5. rescanned immediately before freeze;
6. removed from the exception register when remediation becomes available and is adopted.

### Minimal Runtime

Production runtime images should contain only the software required to operate the released service.

Build-time tools, package installers, development dependencies, test frameworks, source bind mounts, and unused service dependencies must not remain in the final customer runtime unless explicitly justified.

### Non-Root Runtime

USOP-controlled runtime services must run as a non-root user where technically practical.

Any service that cannot run non-root must be documented with the reason and compensating controls.

### Reproducibility

Release dependency versions, base-image identifiers, build inputs, release configuration, and final image digests must be recorded.

Moving tags may be used during pre-freeze patch discovery, but the frozen release must record immutable image identifiers.

## Required Release Gates

### Backend Gate

Required:

- backend regression suite passes;
- runtime dependency integrity passes;
- unused runtime dependencies removed;
- production dependency lock reviewed;
- no unresolved Critical or High vulnerability in USOP-controlled runtime dependencies;
- API image runs as the approved non-root user;
- package-install/build tooling is absent from the final API runtime where not operationally required.

### Frontend Gate

Required:

- full dependency audit passes;
- production-only dependency audit passes;
- lint passes;
- production build passes;
- final runtime image contains compiled assets rather than development source bind mounts;
- no unresolved Critical or High vulnerability in the USOP-controlled web runtime.

Performance warnings such as bundle-size warnings are tracked separately unless they create a material operational or security impact.

### Container Gate

Required for each USOP-controlled image:

- current base-image review;
- image rebuild using the intended release Dockerfile;
- Critical/High CVE scan;
- runtime user verification;
- health validation;
- SBOM generation;
- provenance generation;
- digest capture.

### Deployment Gate

Required:

- release Compose parses successfully;
- PostgreSQL is not published directly to the host by default;
- API is not published directly to the host by default;
- only approved customer-facing ports are published;
- no development bind mounts exist;
- health checks pass;
- web endpoint passes;
- clean-room installation passes before final freeze.

### Secrets Gate

Required:

- no production secret is embedded in source code;
- no production secret is embedded in images;
- no complete customer `.env` is committed;
- the documented RC secret-provider mode matches implementation;
- secret names and configuration behavior are documented;
- logs are reviewed for secret exposure.

### Supply-Chain Gate

Required:

- release SBOM generated;
- provenance generated;
- immutable image digests recorded;
- vulnerability exception register reviewed;
- final release manifest completed;
- release artifacts and customer documentation reconciled.

If a local development tool reports that attestations are missing even though build output shows attestations were generated, that control remains open until the attestation can be independently verified in the final publication workflow.

## Severity Policy

### Critical

A known fixable Critical vulnerability in a USOP-controlled component blocks release.

An unresolved upstream Critical vulnerability requires explicit exception approval and must be rescanned immediately before freeze.

### High

A known fixable High vulnerability in a USOP-controlled component blocks release.

An unresolved upstream High vulnerability requires explicit exception approval and must be tracked to upstream remediation.

### Medium and Low

Medium and Low findings are reviewed and prioritized according to exploitability, exposure, operational impact, and release risk.

They do not automatically block release unless the security review determines the finding creates material risk.

## Release Reopening Conditions

The following changes reopen applicable validation gates:

- application code changes;
- dependency changes;
- lockfile changes;
- base-image changes;
- Dockerfile changes;
- Compose changes;
- `.env` contract changes;
- Graph permission changes;
- authentication changes;
- persistence changes;
- migration changes;
- release documentation changes that affect deployment or security behavior.

## Release Evidence

Every frozen release should retain:

- release version;
- source commit;
- release date;
- dependency locks;
- backend test result;
- frontend audit result;
- frontend lint/build result;
- container scan summary;
- SBOM references;
- provenance references;
- vulnerability exception register;
- image digests;
- clean-room installation result;
- final release manifest.

## Release Approval Principle

> USOP must not become a security liability to the organizations deploying it.

Release security therefore favors reproducible evidence, minimal runtime content, explicit exceptions, and repeatable patching over convenience or optimistic assumptions.
