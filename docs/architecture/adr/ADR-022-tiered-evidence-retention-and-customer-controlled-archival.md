# ADR-022: Tiered Evidence Retention and Customer-Controlled Archival

- **Status:** Accepted
- **Date:** 2026-07-30
- **Decision Makers:** USOP Architecture
- **Supersedes:** None
- **Superseded By:** None

---

# Context

USOP is designed to preserve organizational security knowledge over many years while remaining operationally efficient and scalable.

Organizations using USOP may range from small businesses with fewer than ten employees to global enterprises with hundreds of thousands of identities.

The platform must therefore support long-term retention without requiring unlimited high-performance database storage.

USOP also operates under the principle that customer security data remains under customer control.

The platform must never require customer evidence to be permanently stored in vendor-controlled infrastructure.

---

# Problem

Several categories of information have very different operational characteristics.

Examples include:

- Current identity state
- Historical identity changes
- Organizational decisions
- Decision evidence
- Audit history
- Large evidence artifacts
- Reports
- Archived investigations

Keeping every object indefinitely inside the operational PostgreSQL database would eventually increase storage requirements, reduce query performance, complicate backups, and increase operational costs.

Conversely, immediately removing historical information would weaken auditability and organizational memory.

The platform therefore requires a deterministic retention architecture.

---

# Decision

USOP shall implement a tiered evidence retention architecture.

Operational data remains inside PostgreSQL.

Large or infrequently accessed evidence may be archived into customer-controlled object storage.

USOP continues to present archived information through the same user experience regardless of physical storage location.

---

# Architectural Principles

## Principle 1

PostgreSQL remains the operational source of truth.

Operational intelligence requires fast relational queries.

Current identities, relationships, recommendations, decisions, organizational memory, and searchable metadata remain inside PostgreSQL.

---

## Principle 2

Archived evidence remains customer controlled.

USOP never requires customer evidence to reside within vendor-managed storage.

Customers configure their own archive destination.

Supported archive targets may include:

- Amazon S3
- Azure Blob Storage
- MinIO
- On-premises object storage
- Future supported providers

---

## Principle 3

Operational data and archived evidence are separate concerns.

Operational storage optimizes:

- Query performance
- Relationship traversal
- Decision preparation
- Analyst workflows

Archive storage optimizes:

- Long-term retention
- Low-cost storage
- Legal hold
- Historical retrieval

---

## Principle 4

Archived information remains discoverable.

Analysts should not need to know whether evidence is archived.

Timeline views, searches, investigations, and audit workflows continue to expose archived records through the same interface.

Retrieval location remains an implementation detail.

---

## Principle 5

Evidence integrity must be verifiable.

Every archived object shall maintain metadata sufficient to verify integrity.

Examples include:

- Archive provider
- Object identifier
- Object version
- Content hash
- Content type
- Archive timestamp
- Retention expiration
- Legal hold status

---

## Principle 6

Retention policies belong to the organization.

USOP provides retention capabilities.

Organizations define retention requirements.

Examples include:

- Identity review history
- Decision history
- Audit history
- Evidence packages
- Organizational guidance
- Archived investigations

---

## Principle 7

Trust but verify.

Operational decisions do not automatically modify organizational risk.

Risk posture changes only after subsequent synchronization verifies that remediation occurred.

Decision records therefore represent analyst intent.

Synchronization verifies operational reality.

---

# Storage Model

## Operational Storage

Examples include:

- Identities
- Accounts
- Groups
- Relationships
- Recommendations
- Organizational decisions
- Organizational memory
- Active guidance
- Current audit history

Storage:

PostgreSQL

---

## Warm Historical Storage

Examples include:

- Historical decisions
- Identity deltas
- Review history
- Recommendation history

Storage:

Partitioned PostgreSQL

---

## Archived Storage

Examples include:

- Evidence packages
- Reports
- Attachments
- Investigation exports
- Historical snapshots
- Large artifacts

Storage:

Customer-controlled object storage

---

# Benefits

This architecture provides:

- Long-term scalability
- Operational performance
- Customer ownership
- Lower storage costs
- Improved backup strategy
- Legal hold support
- Simplified enterprise deployment
- Consistent analyst experience

---

# Consequences

Positive

- Operational database remains performant.
- Archived evidence remains available.
- Organizations maintain ownership of sensitive information.
- Storage scales independently of operational workloads.
- Supports deployments ranging from small organizations to large enterprises.

Trade-offs

- Archive retrieval may require additional latency.
- Archive connectors require configuration.
- Additional metadata management is required.
- Archive lifecycle management becomes part of Administration.

---

# Future Work

Future releases may include:

- Archive health monitoring
- Archive verification jobs
- Automatic integrity validation
- Multiple archive providers
- Immutable archive support
- Legal hold workflows
- Archive migration
- Archive search optimization

---

# Decision Summary

USOP preserves operational intelligence inside PostgreSQL while allowing long-term evidence to be archived into customer-controlled storage.

This architecture preserves analyst experience, maintains organizational ownership of security information, supports enterprise-scale retention, and enables long-term organizational memory without sacrificing operational performance.