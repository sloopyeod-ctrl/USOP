# USOP Core v1.0 - Security Deployment Guide

**Document:** 03-Security-Deployment-Guide  
**Release Track:** USOP Core v1.0 Release Candidate  
**Status:** Release Candidate Draft  
**Audience:** Security Engineers, Network Engineers, IAM Engineers, Platform Engineers, Security Architects, Design Partners

## Purpose

This guide defines the security, identity, network, container, storage, and operational review requirements for deploying USOP Core v1.0.

Its goal is to allow a customer security team to review, approve, deploy, and maintain USOP without relying on undocumented developer knowledge.

This guide does not replace the Installation Guide or Secrets Configuration Guide.

Read this guide together with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`

## Security Architecture

USOP Core is an operational decision platform.

USOP consumes authoritative information from external security and identity systems, normalizes that information, creates decision intelligence, and presents organization-aware investigations.

USOP does not replace Microsoft Entra ID as the authoritative identity source.

USOP does not require customer secrets to be embedded in application source code or container images.

USOP should remain deployable using customer-owned credentials, customer-controlled storage, and customer-defined network controls.

## Security Boundary

### USOP Is Responsible For

USOP is responsible for:

- protecting its application configuration;
- maintaining the integrity of its own stored decisions, organizational memory, and platform state;
- limiting credential use to supported operations;
- preventing secret values from being intentionally written to logs or documentation;
- presenting only supported operational truth;
- validating configuration and provider connectivity;
- exposing documented health and operational status;
- preserving tenant or organization boundaries in supported deployment modes.

### Microsoft Entra ID Remains Responsible For

Microsoft Entra ID remains responsible for:

- authoritative identity objects;
- authoritative role assignments;
- authoritative group and directory state;
- authentication and authorization data exposed through Microsoft Graph;
- lifecycle of the customer application registration;
- Microsoft Graph access controls and consent.

### The Customer Is Responsible For

The customer remains responsible for:

- host security;
- Docker/runtime administration;
- network policy;
- firewall policy;
- DNS;
- TLS termination where applicable;
- proxy policy;
- application registration ownership;
- Graph permission approval;
- credential lifecycle;
- secret-provider lifecycle;
- backup policy;
- local logging/monitoring integration;
- vulnerability and patch management for the host platform.

## Network Requirements

The final RC1 package must define the exact inbound and outbound network requirements.

No customer release should rely on undocumented firewall behavior.

### Inbound Access

The release documentation must identify:

- the port used to access the USOP user interface;
- the port or path used for the documented health endpoint;
- whether the backend is exposed directly or only through an application gateway/reverse proxy;
- whether administrative access is required from outside the host.

Only ports required by the frozen release architecture should be exposed.

Do not publish development-only ports as customer requirements unless they are part of the supported release configuration.

### Outbound Access

The release documentation must identify all required outbound destinations.

For Microsoft Entra deployments, this will include the Microsoft identity and Microsoft Graph endpoints required by the validated connector implementation.

If an external secret provider is used, the customer may also need outbound access to the supported provider endpoint.

Exact destinations must be validated against the frozen application before release.

### DNS

The container host and relevant containers must be able to resolve all documented external service endpoints.

If the customer uses internal DNS controls, split DNS, or egress filtering, required destinations should be tested before first synchronization.

### Proxy Support

Proxy behavior must be explicitly documented.

If the frozen release supports HTTP or HTTPS proxy configuration, the exact configuration contract must be recorded before RC1.

If proxy support is not validated, document that limitation rather than implying support.

### Firewall Principle

> Permit only the network paths required by the validated release.

Do not recommend broad outbound access as a workaround.

## TLS and Certificates

USOP customer deployments should use TLS for user-facing access where the application is exposed beyond a trusted local boundary.

The final deployment guide must define whether TLS is terminated by:

- USOP directly;
- a customer reverse proxy;
- an application gateway;
- another supported ingress component.

The customer owns production certificates unless the release explicitly provides a documented certificate-management mechanism.

Do not ship private keys or customer certificates inside the release package.

## Microsoft Entra Requirements

USOP Core v1.0 uses a customer-approved Microsoft Entra application registration.

The customer should provision only the minimum Microsoft Graph permissions required by the frozen RC1 connector.

The customer is responsible for:

- application registration ownership;
- credential creation;
- permission assignment;
- administrator consent where required;
- credential rotation;
- credential revocation when USOP is decommissioned.

USOP must not request broad Graph permissions merely to simplify development.

## Microsoft Graph Permission Matrix

The final RC1 release must include a validated Graph permission matrix.

The current guide intentionally does not invent the final permission set.

The release team must populate this table after inspecting and validating the actual connector calls used by the frozen build.

| Permission | Purpose in USOP | Required in RC1 | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | Must be validated against actual connector behavior |

For every permission included in RC1, document:

- exact Microsoft Graph permission name;
- delegated or application permission type;
- whether administrator consent is required;
- why USOP needs it;
- which connector capability depends on it;
- whether the permission is optional or required.

If a permission is not needed by the frozen RC1 artifact, it should not be requested.

## Least Privilege

USOP should follow least privilege across:

- Entra permissions;
- secret-provider access;
- container runtime access;
- filesystem permissions;
- database permissions;
- host access;
- network access.

Where a credential can be scoped to one secret or one application record, prefer that scope over broad account access.

## Container Security

The final customer container package should define and validate:

- image source;
- image version/tag;
- image digest where practical;
- base image;
- runtime user;
- required Linux capabilities;
- writable paths;
- mounted volumes;
- exposed ports;
- health checks;
- restart policy;
- storage dependencies.

### Runtime User

If the frozen release supports non-root execution, that should be the supported default.

If root is required by any component, the requirement and justification must be documented before release.

### Image Immutability

Customer deployments should use pinned release images.

Do not deploy `latest` tags for the frozen release candidate.

### Image Provenance

The release package should clearly identify where the customer obtains approved USOP images.

If images are provided as archives, checksums should be included.

If images are pulled from a registry, repository, tag, and digest guidance should be included.

## Secrets Management

Secrets are governed by:

```text
02-Secrets-Configuration-Guide.md
```

Core rules:

- secrets remain customer-owned;
- secrets are not committed to source control;
- secrets are not embedded in images;
- `.env.template` contains no working credentials;
- external secret-provider selection is explicit;
- secret provider and secret reference are separate configuration values;
- logs must not intentionally expose secret values.

## Data Storage

USOP is not intended to replace authoritative external systems.

USOP may store operational state required to support its own workflows.

Examples may include:

- normalized platform state required by USOP;
- organizational decisions;
- decision history;
- review scheduling;
- organizational memory;
- knowledge assets;
- platform configuration;
- supported audit information.

The frozen release must document the actual persistent stores used by RC1.

### What USOP Does Not Replace

USOP does not become the authoritative source for:

- Microsoft Entra identities;
- Microsoft Entra groups;
- Microsoft Entra role assignments;
- Microsoft Graph;
- customer secret systems;
- external security platforms.

### Customer-Controlled Archival

Where customer-controlled archival is supported, organizations should be able to retain long-term decisions, audit history, and organizational knowledge in customer-owned storage.

The release must document whether that archival capability is operational in RC1 or planned for a later release.

Do not imply support before it has been validated.

## Database Security

The customer deployment should document:

- database service used by the release;
- network exposure;
- authentication model;
- persistence volume;
- backup method;
- restore method;
- encryption assumptions;
- who should have administrative access.

The database should not be exposed outside the required application boundary unless explicitly required by the supported architecture.

## Logging and Auditing

USOP logs should provide enough information to diagnose operational failures without exposing secrets.

Logs should not intentionally contain:

- client secrets;
- access tokens;
- refresh tokens;
- private keys;
- complete `.env` contents;
- secret-provider credentials.

The release must identify:

- container log locations or commands;
- application log destinations;
- audit log behavior;
- log retention assumptions;
- customer export/integration options if supported.

## Health and Monitoring

The release must document supported monitoring points.

At minimum:

- container state;
- application health endpoint;
- synchronization status;
- provider failures;
- Operational Pulse state.

The current development baseline uses:

```text
GET /health
```

The final customer access path must be validated against the frozen RC deployment.

## Updates and Patch Management

Before customer release:

- backend dependencies must be reviewed and patched as appropriate;
- frontend dependencies must be reviewed and patched as appropriate;
- container base images must be reviewed and patched as appropriate;
- the application must pass the full regression suite after patching;
- the exact passing artifacts must be frozen.

After freeze, any dependency or container-image change reopens validation.

Do not patch the customer release after final validation without creating a new validated release artifact.

## Backup and Recovery

The release must define the customer backup boundary.

At minimum, identify:

- persistent application/database data;
- customer configuration;
- external archival configuration;
- secrets that are intentionally not backed up by USOP;
- restore sequence;
- post-restore validation steps.

The clean-room release process should include a documented recovery test if backup/restore is part of RC1 scope.

## Host Security

The customer remains responsible for securing the Docker host or supported container runtime platform.

Recommended customer controls include:

- operating system patching;
- endpoint protection where applicable;
- administrative access control;
- host firewall;
- time synchronization;
- centralized logging;
- vulnerability management;
- restricted Docker administrative access.

The release package should not require weakening host security controls.

## Reverse Proxy and Ingress

If a reverse proxy or application gateway is part of the supported customer architecture, the release must document:

- supported pattern;
- upstream service destination;
- headers required by the application;
- TLS termination expectations;
- timeout requirements;
- WebSocket behavior if applicable;
- health-check behavior.

If no reverse proxy pattern has been validated, document that limitation.

## Security Validation Before Release

The frozen RC1 artifact must pass the following checks:

- dependency patch review;
- frontend build;
- frontend lint;
- backend regression tests;
- container build;
- container startup;
- health endpoint validation;
- Entra authentication;
- supported identity synchronization;
- secret redaction review;
- port review;
- outbound destination review;
- persistence review;
- clean-room installation.

## Deployment Validation Checklist

Before a customer declares the deployment ready:

- [ ] Approved release version verified.
- [ ] Image source and version verified.
- [ ] Checksums or image integrity verification completed.
- [ ] Required inbound ports approved.
- [ ] Required outbound destinations approved.
- [ ] DNS resolution verified.
- [ ] TLS or approved ingress path verified.
- [ ] Proxy behavior verified if applicable.
- [ ] Entra application registration verified.
- [ ] Minimum Graph permissions verified.
- [ ] Admin consent completed where required.
- [ ] Secret source verified.
- [ ] Secret values absent from distributed artifacts.
- [ ] Container services healthy.
- [ ] Health endpoint healthy.
- [ ] Database persistence verified.
- [ ] Initial synchronization successful.
- [ ] Operational Pulse reflects expected state.
- [ ] Backup responsibility understood.
- [ ] Known Limitations reviewed.

## Security Review Checklist

Security reviewers should be able to answer:

- [ ] What network access does USOP require?
- [ ] What Microsoft Graph permissions does USOP require?
- [ ] Why is each Graph permission required?
- [ ] Where are customer secrets stored?
- [ ] How does USOP retrieve secrets?
- [ ] What data does USOP persist?
- [ ] Which systems remain authoritative?
- [ ] What ports are exposed?
- [ ] How is TLS handled?
- [ ] How are logs protected from secret disclosure?
- [ ] How is the release patched?
- [ ] How is the release rolled back?
- [ ] How is persistent data backed up?
- [ ] How is platform health monitored?
- [ ] What are the known security limitations of RC1?

If any answer depends on undocumented developer knowledge, the release documentation is incomplete.

## Incident and Troubleshooting Hygiene

When collecting diagnostic information:

- sanitize logs;
- never request complete `.env` files;
- never request client secrets;
- never request access tokens;
- never request private keys;
- record the release version;
- record container state;
- record the failing workflow;
- use only the minimum diagnostic data needed.

## Decommissioning

The final customer release should include a decommissioning procedure.

At minimum:

1. stop synchronization;
2. revoke or disable USOP Entra credentials;
3. revoke secret-provider access;
4. stop containers;
5. preserve or export required customer records according to policy;
6. remove customer configuration;
7. remove container images if required;
8. remove persistent storage according to retention policy;
9. verify that external credentials are no longer usable.

## Relationship to Other Customer Documents

Read this guide with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `04-User-Guide.md`
- `07-Release-Notes.md`
- `08-Known-Limitations.md`

The Installation Guide defines deployment sequence.

The Secrets Configuration Guide defines credential handling.

This guide defines the security approval and deployment boundary.

## Release Freeze Requirements

Before RC1 is distributed, replace every unresolved deployment placeholder with validated release data.

At minimum freeze:

- supported host requirements;
- Docker/Compose requirements;
- service names;
- exposed ports;
- outbound destinations;
- proxy support status;
- TLS/ingress pattern;
- Graph permission matrix;
- container runtime user;
- image identifiers;
- database/persistence model;
- log handling;
- backup expectations;
- patch baseline;
- known security limitations.

No customer-facing security requirement should be based on assumption.

## Security Success Criteria

> **A customer security team should be able to review, approve, deploy, monitor, and decommission USOP Core using documented requirements without relying on undocumented developer knowledge or unnecessarily broad privileges.**

If the security boundary is ambiguous, the release is not ready.
