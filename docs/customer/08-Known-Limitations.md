# USOP Core v1.0 - Known Limitations

**Document:** 08-Known-Limitations  
**Release Track:** USOP Core v1.0 Release Candidate  
**Status:** Release Candidate Draft  
**Audience:** Design Partners, Security Leaders, Security Analysts, IAM Teams, Platform Teams, Deployment Teams

## Purpose

This document defines the known boundaries, unsupported scenarios, planned capabilities, and release assumptions for USOP Core v1.0.

Its purpose is to prevent surprises during Design Partner evaluation.

A known limitation is not automatically a defect.

A defect is behavior that contradicts the documented release behavior.

## Release Philosophy

USOP Core v1.0 is intentionally focused.

The release establishes the permanent investigation model and validates that model in realistic customer environments.

Future versions should expand providers and intelligence domains without forcing users to relearn the core workflow.

The objective is evolution rather than replacement.

## Current Scope

RC1 is centered on identity-focused operational intelligence.

The initial supported provider focus is Microsoft Entra ID.

The exact supported connector behaviors, Graph permissions, secret-provider modes, deployment requirements, and runtime assumptions must be frozen against the exact RC artifact before customer distribution.

## Supported Provider Scope

Microsoft Entra ID is the initial provider target for RC1.

The release should not be assumed to support additional identity, cloud, infrastructure, or security providers unless the frozen Release Notes explicitly state that support.

## Planned Providers Not Yet Guaranteed in RC1

Potential future provider expansion includes:

- AWS;
- Google Cloud;
- Okta;
- SecureW2;
- GitHub;
- NetBox;
- Zabbix;
- additional enterprise identity and infrastructure providers.

These are roadmap directions.

They are not operational capabilities until included in a validated release.

## Planned Intelligence Domains

Potential future intelligence domains include:

- Threat Intelligence;
- Vulnerability Intelligence;
- Compliance Intelligence;
- Asset Intelligence;
- CIAM;
- SaaS Governance;
- Cloud Security;
- Endpoint Intelligence.

External publications and authoritative sources such as CISA KEV or DISA content may be available through future licensed extensions.

Core should not imply operational ingestion or analysis of those external publications unless the corresponding capability is licensed and enabled.

## Deployment Limitations

The final RC package must define the exact supported deployment model.

Until deployment validation is complete, do not assume support for:

- every host operating system;
- every Docker version;
- every Docker Compose version;
- every container runtime;
- Kubernetes deployment;
- air-gapped deployment;
- offline installation;
- arbitrary reverse proxies;
- every enterprise ingress controller;
- every proxy configuration;
- every TLS termination pattern.

Only the patterns validated during RC deployment testing should be presented as supported.

## Host Requirements

Final CPU, memory, storage, operating system, Docker, and Compose requirements must be populated from the frozen RC artifact.

Development workstation specifications are not customer support statements.

## Network Limitations

The exact inbound ports, outbound destinations, DNS requirements, and proxy behavior must be validated before RC1 freeze.

Do not assume that broad outbound Internet access is required.

Do not assume that development-only ports are customer-facing requirements.

## Microsoft Graph Permissions

The final Graph permission matrix must be validated against the exact connector calls used by RC1.

No permission should be requested simply because it was convenient during development.

The customer-facing Security Deployment Guide must contain the minimum validated permission set before release.

## Secret Provider Limitations

USOP uses a provider-neutral secret model.

RC1 may not support every secrets manager.

Potential future or customer-relevant providers may include:

- Keeper;
- Azure Key Vault;
- AWS Secrets Manager;
- HashiCorp Vault;
- other supported customer-owned providers.

The frozen release documentation must state exactly which providers are operational.

A UUID or secret reference alone does not identify the provider.

## Environment Secret Mode

Where environment-managed secrets are supported, the customer-owned `.env` file remains sensitive.

USOP does not make an insecure `.env` file secure merely by consuming it.

The customer remains responsible for filesystem permissions, local administrative access, host security, and secret lifecycle.

## Credential Rotation

Final credential reload or restart behavior must be validated during deployment testing.

Do not assume that every rotated credential can be applied without container or service restart.

## Authentication and User Access

The customer-facing release must accurately document the supported platform-user authentication model.

If enterprise SSO, federation, RBAC extensions, or additional authentication mechanisms are not validated in RC1, they must not be implied as supported.

## Organizational Memory Boundaries

USOP preserves organizational decisions and knowledge required by its workflows.

Organizational Experience supports analyst judgment.

Historical decisions must not silently suppress new material security changes.

A new material authorization delta must create a new analyst decision opportunity.

## Review Scheduling Boundaries

Review schedules support periodic reassessment of accepted decisions and governed exceptions.

Scheduled review windows do not suppress immediate review of new material authorization changes.

## Data Authority Boundaries

USOP does not replace authoritative source systems.

Examples include:

- Microsoft Entra ID;
- Microsoft Graph;
- customer secret platforms;
- external security products;
- authoritative cloud or infrastructure systems.

USOP may normalize and persist operational state needed for its own workflows, but source-system authority remains external.

## Storage and Archival Limitations

The final RC documentation must distinguish between:

- active USOP application storage;
- organizational memory retained by USOP;
- customer-controlled external archival;
- source-system data that remains external.

Provider-neutral customer-controlled archival is part of the long-term design direction.

If external archival is not operational in RC1, it must be documented as unavailable rather than implied as complete.

## Backup and Restore

The exact backup and restore process must be frozen during deployment validation.

Do not assume that copying container files alone produces a valid backup.

The release must document the persistent database/configuration boundary and any required post-restore validation.

## Upgrade Limitations

RC1 upgrade support must be explicitly defined.

If upgrading from arbitrary development builds is unsupported, state that clearly.

The final release should define:

- supported source version;
- backup requirements;
- migration behavior;
- configuration changes;
- rollback behavior.

## Rollback Limitations

Rollback may involve more than replacing an application image.

Database migrations, configuration-contract changes, and persistent application state may affect rollback compatibility.

Only the rollback path validated for RC1 should be documented as supported.

## UI Limitations

The customer release may contain intentional progressive disclosure and compact panels.

Collapsed information is not necessarily unavailable.

The interface should prioritize operational decisions over exhaustive detail.

If an expected capability is not visible, first confirm whether it exists behind supported expansion or detail controls before classifying the behavior as missing.

## Screenshot and Documentation Drift

Screenshots in the User Guide and README must match the frozen RC1 interface.

Until screenshot freeze is complete, placeholder images or development screenshots should not be treated as final customer documentation.

## Performance Expectations

Final performance expectations must be based on validation, not intuition.

RC1 should be tested for:

- dashboard responsiveness;
- investigation load time;
- graph responsiveness;
- synchronization performance;
- container resource usage;
- database behavior.

No unsupported performance SLA should be implied.

## Scale Limitations

The maximum validated organization size, identity count, graph size, synchronization volume, and decision-history volume must be determined through RC validation.

Until measured, do not claim unlimited enterprise scale.

## Error Handling Limitations

Customer-facing error states should explain the problem, operational impact, and next action.

If a failure still exposes implementation-heavy output or requires developer-only troubleshooting, it should be treated as an RC readiness issue.

## Logging Limitations

Logs must not intentionally expose secrets.

However, customers remain responsible for protecting their local logging systems and access to container logs.

The final release should document known logging destinations and retention assumptions.

## Monitoring Limitations

The current operational monitoring model includes the application health endpoint, container state, synchronization state, and Operational Pulse where supported.

If direct integration with external monitoring platforms is not validated in RC1, it should not be implied as supported.

## Reporting Limitations

Enterprise reporting, executive exports, scheduled reporting, or other future reporting capabilities may not be part of RC1 unless explicitly listed in the frozen Release Notes.

## AI and Automation Boundaries

USOP Core should not be assumed to provide an autonomous AI analyst unless that capability is explicitly released.

Decision Intelligence is intended to remain explainable and governed.

Automation must not silently replace required analyst decisions for material security changes.

## Licensing and Extension Boundaries

Future capabilities may be delivered as optional licensed extensions.

Core may support linking external publications or capabilities without operationalizing them.

A licensed extension may be required before USOP ingests, analyzes, correlates, or acts on certain external intelligence sources.

The frozen customer package must state which capabilities are included under the evaluated license.

## Design Partner Program Boundaries

Design Partners are evaluating the product.

They are not expected to:

- patch the application independently;
- modify the source code;
- broaden Entra permissions beyond the documented release;
- bypass security controls to make the product work;
- redistribute release artifacts outside the participating organization;
- expose secrets during troubleshooting.

Unexpected behavior should be reported through the Design Partner process.

## Known Limitation vs Defect

Use this distinction:

### Known Limitation

A behavior or capability boundary that is accurately documented and accepted for RC1.

### Defect

Behavior that:

- contradicts the documented release;
- breaks a supported workflow;
- exposes incorrect operational truth;
- creates a security or data-integrity risk;
- prevents supported deployment or normal use.

## Reporting Unexpected Behavior

When reporting an unexpected condition, provide:

```text
Release Version:
Build / Image Identifier:
Page / Workflow:
Expected Behavior:
Observed Behavior:
Operational Impact:
Reproduction Steps:
Sanitized Evidence:
```

Do not include:

- client secrets;
- access tokens;
- refresh tokens;
- private keys;
- complete `.env` files;
- secret-provider credentials.

## Customer Responsibilities

The customer remains responsible for:

- host operating system security;
- Docker/runtime security;
- firewall and egress policy;
- DNS;
- TLS certificates and ingress where applicable;
- Entra application ownership;
- Graph permission approval;
- credential rotation;
- secret-provider security;
- backup policy;
- retention policy;
- access to logs and persistent storage;
- local vulnerability and patch management.

USOP should not require weakening these controls.

## RC1 Freeze Review

Before this document is considered final, reconcile it against the exact frozen artifact.

Remove any limitation that no longer applies.

Add any limitation discovered during:

- dependency patching;
- regression testing;
- container validation;
- clean-room installation;
- performance validation;
- security review;
- Design Partner packaging.

Populate final statements for:

- supported providers;
- supported secret providers;
- host requirements;
- runtime versions;
- ports;
- network destinations;
- Graph permissions;
- scale boundaries;
- performance expectations;
- backup/restore;
- upgrade/rollback;
- authentication model;
- known UI limitations.

## Relationship to Other Customer Documents

Read this document with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `04-User-Guide.md`
- `05-Design-Partner-Guide.md`
- `06-Feedback-Questionnaire.md`
- `07-Release-Notes.md`

Release Notes explain what RC1 includes.

This document explains the boundaries of that release.

## Limitation Management Principle

> **Customers should encounter documented boundaries, not surprises.**

If a limitation can materially affect deployment, security, trust, or the investigation workflow, it must be documented before the release is distributed.

## Release Success Criteria

> **USOP Core v1.0 RC1 is ready for Design Partner delivery only when its supported capabilities and known boundaries are both documented accurately enough that a customer can evaluate the product without discovering material surprises through trial and error.**

If an important limitation is known but undocumented, the release is not ready.
