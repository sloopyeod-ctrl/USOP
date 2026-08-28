# USOP Core - Installation Guide

**Document:** 01-Installation-Guide
**Release:** 0.14.0-dp2-final
**Release Stage:** Design Partner Release Candidate
**Status:** Frozen Design Partner Documentation
**Audience:** System Administrators, Security Engineers, Platform Engineers, Design Partners

## Purpose

This guide defines the validated first-time installation procedure for USOP Core 0.14.0-dp2-final.

The procedure is based on the clean-room installation performed against the frozen Design Partner package. It does not require the USOP source tree, development virtual environment, source build contexts, or developer workstation state.

## Installation Principle

USOP is distributed as frozen Docker image archives plus a customer deployment contract.

Customer-specific credentials and configuration are supplied by the customer and are not embedded in the release images or documentation.

Do not substitute source-built images or development Compose files for the artifacts supplied in the Design Partner package.

## Required Administrative Access

The deployment team must be able to:

- administer the target Docker host;
- create and protect local deployment configuration;
- load supplied Docker image archives;
- configure local firewall, DNS, proxy, and TLS policy;
- create or approve required Microsoft Entra application configuration;
- provide customer-owned credentials;
- verify application health.

Routine installation should not require USOP developer assistance.

## Validated Package Layout

```text
USOP-Core-0.14.0-dp2-final/
|-- .env.release.example
|-- CHECKSUMS.sha256
|-- docker-compose.yml
|-- VERSION
|-- docs/
|   |-- 01-Installation-Guide.md
|   |-- 02-Secrets-Configuration-Guide.md
|   |-- 03-Security-Deployment-Guide.md
|   |-- 04-User-Guide.md
|   |-- 05-Design-Partner-Guide.md
|   |-- 06-Feedback-Questionnaire.md
|   |-- 07-Release-Notes.md
|   -- 08-Known-Limitations.md
-- images/
    |-- usop-core-api-0.14.0-dp2-final.tar
    |-- usop-core-postgres-0.14.0-dp2-final.tar
    -- usop-core-web-0.14.0-dp2-final.tar
```

Stop if any required package component is missing.

## Step 1 - Verify Package Integrity

Before loading images or creating configuration, verify every file against CHECKSUMS.sha256.

Do not continue when a required file is missing or its SHA-256 digest does not match the supplied manifest.

## Step 2 - Load the Frozen Images

Load all three supplied image archives:

```powershell
docker load -i .\images\usop-core-api-0.14.0-dp2-final.tar
docker load -i .\images\usop-core-web-0.14.0-dp2-final.tar
docker load -i .\images\usop-core-postgres-0.14.0-dp2-final.tar
```

The expected image tags are:

```text
usop-core-api:0.14.0-dp2-final
usop-core-web:0.14.0-dp2-final
usop-core-postgres:0.14.0-dp2-final
```

The supplied docker-compose.yml references these frozen images and contains no customer-side build contexts.

## Step 3 - Create Customer Configuration

Copy the supplied environment template:

```powershell
Copy-Item .env.release.example .env.release
```

Replace every required CHANGE_ME value with customer-owned configuration.

Do not modify .env.release.example with real credentials. Treat .env.release as sensitive deployment configuration.

Before entering credentials, read 02-Secrets-Configuration-Guide.md.

## Step 4 - Configure Required Release Values

The frozen customer deployment requires values for:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
USOP_SECRET_PROVIDER

MS_GRAPH_TENANT_ID
MS_GRAPH_CLIENT_ID
MS_GRAPH_CLIENT_SECRET

USOP_AUTH_ENTRA_TENANT_ID
USOP_AUTH_ENTRA_AUDIENCE
USOP_AUTH_ENTRA_REQUIRED_SCOPE

USOP_WEB_PORT
```

For this Design Partner release:

```text
USOP_SECRET_PROVIDER=env
USOP_AUTH_ENTRA_REQUIRED_SCOPE=access_as_user
```

Generate a unique high-entropy PostgreSQL password. Do not reuse examples, validation passwords, or credentials from another environment.

Microsoft Graph credentials and inbound USOP API authentication are separate trust boundaries. See the Secrets Configuration Guide.

## Step 5 - Review Network and Security Requirements

Before startup, read 03-Security-Deployment-Guide.md.

The validated network contract is:

- publish only the USOP web ingress using USOP_WEB_PORT, default TCP 8080;
- do not publish API TCP 8000;
- do not publish PostgreSQL TCP 5432;
- permit required API egress to Microsoft identity and Graph endpoints over TCP 443;
- provide DNS resolution for required Microsoft endpoints;
- use customer-controlled TLS termination for network-accessible deployments;
- do not open additional ports merely to simplify installation.

Direct HTTP access to the web port is intended only for an accepted local or isolated evaluation boundary.

## Step 6 - Validate Compose Configuration

From the package directory run:

```powershell
docker compose -f docker-compose.yml --env-file .env.release config
```

This command must complete successfully before startup.

Missing required values must be corrected rather than replaced with fake placeholders.

## Step 7 - Start USOP

Run:

```powershell
docker compose -f docker-compose.yml --env-file .env.release up -d
```

The validated startup sequence is:

```text
PostgreSQL healthy
        |
        v
migrate: alembic upgrade head
        |
        v
API healthy
        |
        v
Web healthy
```

The migrate service is intentionally one-shot and should exit with code 0 after the schema reaches the release head.

## Step 8 - Verify Container State

Run:

```powershell
docker compose -f docker-compose.yml --env-file .env.release ps -a
```

Expected state:

```text
postgres   Up (healthy)
migrate    Exited (0)
api        Up (healthy)
web        Up (healthy)
```

Repeated restarts, unhealthy services, or a non-zero migration exit require investigation before use.

## Step 9 - Verify Application Routes

Using the configured USOP_WEB_PORT, verify:

```text
GET /
GET /health
GET /ready
```

The clean-room acceptance deployment returned HTTP 200 from all three routes.

The health response reported USOP runtime version 0.14.0 and the readiness response reported the API ready.

## Step 10 - Verify Database Migration

The frozen Design Partner schema head is:

```text
a71d9c4e2b63
```

A fresh validated installation produced 27 public PostgreSQL tables and contained no preloaded customer operational data.

Customers normally do not need to query PostgreSQL directly during routine installation. These values are release-validation references for troubleshooting and support.

## Step 11 - Open the User Interface

Open the USOP web URL using the configured host and USOP_WEB_PORT.

For a local isolated deployment using the default port:

```text
http://localhost:8080/
```

For network-accessible deployments, use the customer-controlled TLS access path defined by the Security Deployment Guide.

## Step 12 - Microsoft Entra Configuration

This release uses Microsoft Entra for two distinct purposes:

1. outbound Microsoft Graph collection by USOP;
2. inbound delegated authentication of callers to the USOP API.

Both configuration groups are required by the frozen customer Compose contract.

Do not automatically substitute Graph client configuration for the inbound API audience.

See 02-Secrets-Configuration-Guide.md and 03-Security-Deployment-Guide.md.

## Restart Behavior

A normal Docker Compose restart was validated against the clean-room deployment.

After restart:

- PostgreSQL returned healthy;
- the migration service completed with exit code 0;
- the schema remained at a71d9c4e2b63;
- API and Web returned healthy;
- /health returned HTTP 200;
- /ready returned HTTP 200;
- the fresh operational database remained unchanged.

## Runtime Security Characteristics

The customer deployment contract preserves the release hardening controls:

- API runs as the non-root usop user;
- Web runs as the non-root nginx user;
- API and Web root filesystems are read-only;
- all Linux capabilities are dropped from API and Web;
- privilege escalation is disabled;
- API /tmp is a controlled writable tmpfs;
- API and PostgreSQL are internal-only by default.

## Troubleshooting Principles

When installation fails:

1. stop at the failing layer;
2. verify package integrity;
3. verify .env.release configuration without printing secrets;
4. run docker compose config;
5. inspect docker compose ps -a;
6. inspect only the logs needed for the failed service;
7. verify DNS and required outbound connectivity;
8. verify Entra application configuration and consent;
9. do not weaken security controls merely to make the stack start.

Never include .env.release, access tokens, client secrets, or other credentials in support bundles.

## Clean-Room Acceptance

USOP Core 0.14.0-dp2-final passed clean-room installation from the packaged Docker archives using a fresh Compose project and fresh PostgreSQL volume.

The validation did not require the source tree or development build contexts.

## Installation Success Criteria

Installation is successful when:

- package checksums are verified;
- all three frozen images are loaded;
- required customer configuration is populated;
- Compose configuration validates;
- PostgreSQL is healthy;
- migration exits 0;
- API is healthy;
- Web is healthy;
- /health returns HTTP 200;
- /ready returns HTTP 200;
- the expected release is displayed;
- no undocumented developer state is required.

## Next Documents

- 02-Secrets-Configuration-Guide.md
- 03-Security-Deployment-Guide.md
- 04-User-Guide.md
- 05-Design-Partner-Guide.md
- 06-Feedback-Questionnaire.md
- 07-Release-Notes.md
- 08-Known-Limitations.md
