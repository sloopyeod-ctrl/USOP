# USOP Core v1.0 - Installation Guide

**Document:** 01-Installation-Guide  
**Release Track:** USOP Core v1.0 Release Candidate  
**Status:** Release Candidate Draft  
**Audience:** System Administrators, Security Engineers, Platform Engineers, Design Partners

## Purpose

This guide defines the first-time installation workflow for USOP Core v1.0.

Its goal is to allow an administrator who has never deployed USOP to install the release package, verify platform health, and proceed to identity-provider configuration without developer assistance.

This guide intentionally does not duplicate the Secrets Configuration Guide or Security Deployment Guide. Those documents provide the detailed credential and network/security requirements referenced here.

## Expected Outcome

At the end of this guide, the administrator should have:

- obtained the approved USOP Core release package;
- prepared the host environment;
- created customer-owned configuration from the provided template;
- started the USOP containers;
- verified container and application health;
- opened the USOP user interface;
- confirmed the expected release version;
- reached the point where Microsoft Entra ID can be configured.

The installation is not considered complete until health verification succeeds.

## Installation Principle

USOP Core is intended to be delivered as a repeatable, environment-neutral container deployment.

The distributed release package must not contain customer credentials, development credentials, developer tenant identifiers, test secrets, machine-specific filesystem paths, or undocumented environment assumptions.

Customer-specific values are supplied during deployment.

## Before You Begin

Do not begin installation until the release package includes the final versions of:

- container image or image references;
- Docker Compose configuration;
- `.env.template`;
- Secrets Configuration Guide;
- Security Deployment Guide;
- Release Notes;
- Known Limitations;
- release version identifier;
- release checksums.

If any required release artifact is missing, stop and obtain the complete release package.

## Required Administrative Access

The deployment team should identify personnel able to:

- administer the target container host;
- create and manage local deployment files;
- configure required network access;
- create or approve Microsoft Entra application access;
- provide customer-owned secrets or secret references;
- validate local firewall, proxy, DNS, and TLS requirements.

USOP should not require a developer to perform routine customer installation.

## Supported Deployment Model

USOP Core v1.0 uses a Docker-based deployment model.

The release package is expected to provide a Docker Compose configuration that defines the supported USOP services and their relationships.

The exact supported host operating systems, Docker versions, Compose versions, minimum CPU, memory, storage, and exposed ports must be frozen during the RC deployment-validation phase and recorded in this guide before customer release.

**Do not infer unsupported requirements from a developer workstation.**

## Release Package Layout

The final customer package should follow a predictable structure similar to:

```text
USOP-Core-v1.0-RC1/
|
|-- README.md
|-- docker-compose.yml
|-- .env.template
|-- VERSION
|-- CHECKSUMS
|
|-- docs/
|   `-- customer/
|       |-- 01-Installation-Guide.md
|       |-- 02-Secrets-Configuration-Guide.md
|       |-- 03-Security-Deployment-Guide.md
|       |-- 04-User-Guide.md
|       |-- 05-Design-Partner-Guide.md
|       |-- 06-Feedback-Questionnaire.md
|       |-- 07-Release-Notes.md
|       `-- 08-Known-Limitations.md
|
`-- sample-config/
```

## Step 1 - Verify the Release Package

Before changing configuration, verify that the release package is complete.

Confirm that the expected release version, checksums, required documentation, `.env.template`, and Compose file are present and that no customer or developer secrets are embedded in distributed files.

## Step 2 - Prepare a Deployment Directory

Create a dedicated directory for the USOP deployment.

Maintain customer-specific configuration separately from immutable release artifacts whenever practical.

## Step 3 - Create Customer Configuration

Copy the distributed environment template to the customer configuration file expected by the release package.

Example pattern:

```text
.env.template  ->  .env
```

Do not place real credentials into `.env.template`.

Before adding secrets, read:

```text
02-Secrets-Configuration-Guide.md
```

Where external secret-provider references are supported, the provider and secret reference should be configured explicitly rather than assuming that a UUID identifies a particular secrets platform.

## Step 4 - Review Security and Network Requirements

Before starting the application, read:

```text
03-Security-Deployment-Guide.md
```

Confirm the frozen Core v1.0 network contract before startup:

- publish only the USOP web ingress using the configured USOP_WEB_PORT, default TCP 8080;
- do not publish API TCP 8000;
- do not publish PostgreSQL TCP 5432;
- permit outbound TCP 443 from the API runtime to login.microsoftonline.com;
- permit outbound TCP 443 from the API runtime to graph.microsoft.com;
- provide DNS resolution for both Microsoft destinations;
- use customer-controlled TLS termination ahead of USOP for network-accessible deployments;
- do not assume explicit HTTP or HTTPS proxy support;
- do not require broad unrestricted Internet egress.

Direct HTTP access to TCP 8080 is intended only for an accepted local or isolated evaluation boundary.

Do not open additional ports or permit broad outbound access merely to make deployment easier.

## Step 5 - Validate Configuration Before Startup

The final release process should include a configuration-validation step before operational synchronization begins.

At minimum, validate that:

- all required non-secret values are present;
- the selected secret mode is valid;
- required secret values or secret references are present;
- container configuration can be parsed;
- required port mappings do not conflict;
- storage locations are available;
- required release files exist.

The exact validation command will be frozen during RC-002 deployment packaging.

**Customer release must not require administrators to discover configuration errors through application stack traces.**

## Step 6 - Pull or Load the Approved Images

Use only the container images identified by the approved release package.

The exact command depends on the final distribution method selected during RC packaging.

For registry-based distribution, Docker Compose will obtain the pinned release images.

For offline or controlled-environment distribution, the release may instead provide approved image archives and corresponding checksums.

## Step 7 - Start USOP Core

The final deployment is expected to use Docker Compose.

The target startup pattern is:

```powershell
docker compose up -d
```

Do not treat this command alone as proof of successful installation.

Proceed immediately to health verification.

## Step 8 - Verify Container State

Confirm that all services defined by the release Compose file are running as expected.

Unexpectedly stopped or repeatedly restarting containers must be resolved before proceeding.

## Step 9 - Verify Application Health

USOP includes an application health endpoint.

The current development baseline has used:

```text
GET /health
```

and has returned application health and version information.

For the customer release, verify that the frozen deployment exposes the documented health endpoint through the supported access path.

The expected result must show a healthy platform state and the expected USOP Core release version.

Do not continue if the application reports an unhealthy state or an unexpected version.

## Step 10 - Open the User Interface

Open the documented USOP application URL in a supported browser.

A successful first launch should present the USOP interface without blank pages, unresolved API errors, development-only banners, or developer tenant data.

## Step 11 - Confirm the Initial Operational View

For an environment that has not yet completed provider configuration, the interface should present an intentional empty or configuration-required state rather than fabricated operational data.

USOP must never present synthetic customer health, connector health, identities, or investigation results as if they were observed operational truth.

## Step 12 - Configure Microsoft Entra ID

Do not place Entra credentials directly into source code, Compose files, screenshots, documentation, or shared messages.

Continue with:

```text
02-Secrets-Configuration-Guide.md
```

and:

```text
03-Security-Deployment-Guide.md
```

Those guides will define tenant and application identifiers, supported secret-source modes, credential/reference handling, required Microsoft Graph permissions, admin-consent expectations, network destinations, and least-privilege guidance.

## Step 13 - Verify Provider Connectivity

After Entra configuration is complete, use the documented synchronization or provider-validation workflow.

The release is not operationally ready until USOP can authenticate using the configured customer-owned secret path, reach required Microsoft endpoints, collect supported identity information, synchronize without exposing credentials, and surface a successful operational state.

## Step 14 - Begin the First Investigation

Once provider synchronization is healthy, proceed to the USOP user workflow:

```text
Executive Dashboard
        |
        v
Open Investigation
        |
        v
Mission Brief
        |
        v
Decision Intelligence
        |
        v
Organizational Experience
        |
        v
Organizational Decision
        |
        v
Operational Pulse
```

For product usage instructions, continue to:

```text
04-User-Guide.md
```

## Health Verification Standard

Installation is successful only when all applicable checks pass:

- [ ] Release version matches the approved package.
- [ ] Required containers are running.
- [ ] Health endpoint reports healthy.
- [ ] UI loads successfully.
- [ ] No development credentials or tenant data are present.
- [ ] Customer configuration loads without exposed secrets.
- [ ] Provider authentication succeeds after configuration.
- [ ] Initial synchronization completes successfully.
- [ ] Operational Pulse reports an expected state.
- [ ] First investigation can be opened.

## Troubleshooting Principles

Use this order:

1. Verify release version.
2. Verify container state.
3. Verify health endpoint.
4. Verify configuration completeness.
5. Verify network access.
6. Verify secret-source access.
7. Verify Entra application configuration.
8. Review application logs for the failing service.
9. Consult Known Limitations.
10. Escalate with sanitized diagnostic information.

Never send credentials, tokens, `.env` contents, or private keys as troubleshooting evidence.

## Common Installation Failure Categories

### Container Does Not Start

Check image availability, Compose syntax, port conflicts, storage permissions, and missing required configuration.

### Health Endpoint Is Unhealthy

Check dependent services, database connectivity, startup logs, configuration validation, and expected release version.

### UI Cannot Reach Backend

Check documented port mappings, reverse proxy configuration if applicable, browser/network path, frontend API configuration, and container network state.

### Entra Authentication Fails

Do not rotate or broaden permissions blindly.

Validate tenant identifier, application/client identifier, secret or secret reference, secret-provider access, configured Graph permissions, admin consent, and outbound connectivity.

### Synchronization Completes With No Expected Data

Confirm that the application registration has the documented permissions and that the test organization contains supported objects.

Do not assume an empty result indicates a successful production configuration.

## Clean-Room Installation Requirement

Before USOP Core v1.0 RC1 is provided to a design partner, the final release package must be installed on a clean host using only the customer-facing release package and documentation.

The person performing the clean-room installation should not rely on undocumented developer knowledge, source-tree configuration, previously created local secrets, development database state, VS Code setup, or developer-specific environment variables.

Any missing instruction discovered during clean-room installation must be corrected before release freeze.

## Release Freeze Requirement

The exact artifact that passes clean-room installation and final regression testing becomes the release candidate.

After freeze, no dependency updates, container-image changes, deployment-behavior documentation changes, configuration-contract changes, or application code changes may be introduced without reopening validation.

## Next Documents

Continue in this order:

1. `02-Secrets-Configuration-Guide.md`
2. `03-Security-Deployment-Guide.md`
3. `04-User-Guide.md`
4. `05-Design-Partner-Guide.md`
5. `06-Feedback-Questionnaire.md`
6. `07-Release-Notes.md`
7. `08-Known-Limitations.md`

## Installation Success Criteria

> **A design partner who has never installed USOP should be able to deploy the approved release package, verify platform health, and reach provider configuration without developer assistance.**

If that outcome cannot be achieved, the release is not ready.
