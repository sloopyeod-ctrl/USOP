# ADR-027: Tenant, Organization, and Connector Ownership Architecture

- **Status:** Accepted
- **Date:** 2026-08-02
- **Decision Makers:** USOP Architecture
- **Supersedes:** None
- **Superseded By:** None

---

# Context

USOP must support the same architecture for a small company operating one security environment and for an MSP, MSSP, integrator, or enterprise operating hundreds of isolated customer environments.

The platform must preserve strict organizational isolation while allowing explicitly authorized parent-level administrators and analysts to work across the Organizations they manage. USOP must also support optional commercial modules without creating separate ownership models for each module or deployment size.

Connector ownership is central. Microsoft Entra ID, Zabbix, NetBox, AWS, GCP, Okta, SecureW2, and future providers must never send data into an unscoped global synchronization process. USOP must know the authoritative Organization before collection, normalization, reconciliation, governance, or decision intelligence begins.

USOP applies the KISS principle:

> Keep It Simple, Stupid.

Complex deployment sizes must not require different ownership models or special-case code paths.

---

# Decision

USOP adopts this permanent ownership hierarchy:

```text
USOP Platform
    |
    v
Tenant
    |
    v
Organization
    |
    v
Connector
    |
    v
Collected and Derived Data
```

The same hierarchy applies whether a deployment contains one Organization or hundreds.

---

# Platform

A Platform represents one deployed USOP instance. It is responsible for platform lifecycle, upgrades, global configuration, installed modules, deployment health, licensing enforcement, and explicitly authorized cross-Organization administration.

---

# Tenant

A Tenant represents the commercial or contractual owner of the deployment.

Examples include a small company, Booz Allen Hamilton, a city government, a hospital system, or an MSSP.

A Tenant owns:

- the commercial relationship;
- the Tenant license;
- licensed Organization capacity;
- enabled commercial modules;
- Tenant-level administrators;
- the Organizations created beneath it.

The Tenant is not the primary operational data-isolation boundary. The Organization is.

---

# Organization

An Organization is the primary operational security and data-isolation boundary in USOP.

An Organization owns or governs:

- Organizational Identities;
- Accounts;
- Groups and memberships;
- Roles and role assignments;
- Access Reviews and Review Campaigns;
- Governance Policies;
- Decision Records;
- Organizational Memory;
- Reviewer Workbench queues;
- Operational Attention;
- Connector configurations;
- collected provider data;
- future module data.

Users assigned only to one Organization must not be able to view, query, export, correlate, or act on another Organization's data. Tenant-level users may access multiple Organizations only when their authorization explicitly grants that scope.

---

# Connector

Every Connector belongs to exactly one Organization.

A Connector configuration contains or resolves to:

- Connector ID;
- Organization ID;
- provider type;
- provider-specific configuration;
- secret reference;
- synchronization schedule;
- enabled state;
- health state;
- last successful synchronization time;
- next scheduled synchronization time;
- permitted licensed capabilities.

A Connector may not operate without an Organization owner and may not write collected data into another Organization. Reassigning a Connector must be an explicit, auditable administrative action.

---

# Connector-Originated Ownership

Every object collected by a Connector inherits the Connector's Organization context before normalization or reconciliation begins.

```text
Tenant
    |
    v
Organization
    |
    v
Connector
    |
    v
Collection
    |
    v
Normalization
    |
    v
Reconciliation
    |
    v
Governance and Decision Intelligence
```

USOP must never infer organizational ownership from display names, usernames, email domains, source identifiers, provider tenant names, deployment size, the number of Organizations, the first matching record, or a default Organization.

Ownership originates from the Organization-owned Connector.

---

# Identity Placement

A trusted Organization-owned Connector may establish authoritative placement context for newly collected identities.

USOP may support Organization-specific modes:

- require analyst approval;
- automatically place identities from a trusted Organization-owned Connector;
- apply an approved Organization placement rule.

Automatic placement is not inference when it derives from explicit Connector ownership. Placement evidence must preserve Organization ID, Connector ID, provider, source identifier, placement mode, actor or system principal, timestamp, and governing policy or approved rule.

A canonical person may participate in more than one Organization. Each participation uses a separate Organizational Identity.

---

# Synchronization Scheduling

Synchronization cadence belongs to the Connector configuration.

Approved schedules may include manual, every 15 minutes, hourly, every 4 hours, every 12 hours, daily, or an approved custom schedule.

Synchronization jobs load the Connector, obtain its Organization context, and construct synchronization and reconciliation using that context. Production callers must not require operators to remember or guess an Organization ID.

---

# Authorization

Authorization follows ownership.

```text
Platform Administrator
    +-- explicitly granted platform scope

Tenant Administrator
    +-- all or selected Organizations

Organization Administrator
    +-- one assigned Organization

Organization Analyst
    +-- one or more explicitly assigned Organizations
```

Repository and service operations must enforce scope. Frontend filtering alone is not an authorization boundary. Parent visibility must result from explicit authorization, not global unscoped queries.

---

# Licensing

Licensing follows Tenant and Organization ownership.

A Tenant license may define licensed Organization capacity, commercial edition, enabled modules, feature entitlements, seat limits, effective and expiration dates, deployment identifier, and commercial purpose.

Organizations consume licensed Organization capacity. Connectors do not introduce a separate ownership hierarchy. Modules may be enabled for all licensed Organizations or selected Organizations according to the commercial agreement.

---

# Commercial Modules

Core and optional modules reuse the same ownership model. Examples include Identity Governance, Decision Intelligence, Organizational Memory, Threat Intelligence, Vulnerability Intelligence, Asset Intelligence, Cloud Security, CIAM, SaaS Governance, Compliance, CISA KEV, DISA STIG, Zero Trust, and future AI-assisted capabilities.

No module may introduce a competing tenant hierarchy.

Each module must answer:

1. Which Tenant owns the licensed capability?
2. Which Organization owns the operational data?
3. Which Connector or governed source produced the data?
4. Which authorized users may view or act on it?

---

# Small-Customer Experience

A small customer may operate one Tenant, one Organization, and several Connectors. The product may hide unnecessary hierarchy in the UI while preserving the same internal ownership model. No separate small-business architecture is required.

---

# MSP and MSSP Experience

A large provider may operate one Tenant with hundreds of Organizations. Authorized parent analysts may work across assigned Organizations, while customer Organization users remain isolated to their own Organization.

The same models, services, APIs, and UI patterns are used at every deployment size.

---

# KISS Architectural Rule

> Tenant owns the commercial relationship. Organization owns the operational security boundary. Connector owns collection context. Data inherits that context.

The customer-facing model remains:

```text
Tenant
    |
    v
Organization
    |
    v
Connector
    |
    v
Data
```

If a proposed feature requires a competing ownership hierarchy, implicit ownership inference, or deployment-size-specific code paths, the design must be reconsidered before implementation.

---

# Security Requirements

This architecture requires fail-closed Organization scoping, no implicit cross-Organization joins, no unscoped Connector execution, no ownership inference after collection, explicit authorization for parent visibility, auditable Connector reassignment, Organization-aware synchronization and reconciliation, Organization-aware governance and analyst work, preserved Connector lineage, secure secret references, and no secrets in logs, APIs, reports, or frontend payloads.

USOP must be the security example, not the security exception.

---

# Relationship to Existing ADRs

This ADR extends and governs the application of ADR-017, ADR-019, ADR-024, ADR-025, and ADR-026.

ADR-025 and ADR-026 remain valid. ADR-027 establishes the Tenant above the Organization and makes Organization-owned Connectors the authoritative origin of collected-data ownership.

---

# Implementation Sequence

Implementation proceeds in small, beta-focused slices:

1. preserve the current Organization-aware identity workflow;
2. add the Tenant model and Tenant-to-Organization ownership;
3. add Organization-owned Connector configuration;
4. derive synchronization context from Connector ownership;
5. update scheduling and Connector health by Organization;
6. migrate governance and analyst work to explicit Organization ownership;
7. enforce Tenant and Organization module entitlements;
8. add parent-level frontend views with explicit authorization;
9. retain the simple single-Organization experience.

No slice should delay V1/beta for speculative features unrelated to the end-to-end identity governance workflow.

---

# Consequences

## Positive

- one architecture supports one or hundreds of Organizations;
- ownership is deterministic before collection;
- small customers receive a simple experience;
- MSP and MSSP customers receive scalable isolation and oversight;
- licensing is understandable;
- optional modules fit naturally;
- synchronization becomes safer;
- Connector development becomes consistent;
- customer onboarding and training become easier.

## Tradeoffs

- a Tenant foundation must be introduced;
- existing Organizations require Tenant ownership;
- current live tools passing Organization IDs must migrate to Connector-derived context;
- repositories and services must enforce Organization scoping;
- parent authorization requires careful explicit design;
- Connector reassignment requires strong controls and audit evidence.

These tradeoffs are accepted because they prevent greater long-term complexity and cross-Organization security risk.

---

# Decision Summary

USOP will use one simple ownership model at every deployment size:

```text
Tenant
    |
    v
Organization
    |
    v
Connector
    |
    v
Data
```

The Tenant owns licensing and commercial capacity. The Organization owns operational security and data isolation. The Connector owns collection context and scheduling. All collected and derived data inherits the Organization context established by the Connector.

This model is the permanent architectural foundation for USOP Core and all future commercial modules.
