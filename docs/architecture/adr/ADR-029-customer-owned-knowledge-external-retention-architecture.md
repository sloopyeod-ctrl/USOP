# ADR-029: Customer-Owned Knowledge & External Retention Architecture

**Status:** Accepted

## Context

USOP is an intelligence platform, not the permanent owner of customer
knowledge. Organizations retain ownership of their decisions, evidence,
governance history, audit records, and institutional knowledge
regardless of where those artifacts are physically stored.

This ADR establishes a permanent architectural principle:

> **USOP shall never become the exclusive owner of customer
> institutional knowledge.**

## Decision

Customers always own:

-   Decision Records
-   Knowledge Assets
-   Authorization Events
-   Evidence Snapshots
-   Governance References
-   Audit History
-   Archive Packages

USOP owns:

-   Relationship models
-   Intelligence engines
-   Recommendation engines
-   Workflow orchestration
-   Visualization
-   Reasoning services

## Architectural Principles

1.  Customer Ownership
2.  Intelligence over Storage
3.  Provider Neutrality
4.  Operational vs Archive Separation
5.  Exportability

## Operational Layer

-   Pending Work
-   Active Decisions
-   Active Organizational Memory
-   Relationship Indexes

## Archive Layer

Customer-controlled historical packages referenced through a
provider-neutral ArchiveProvider abstraction.

## USOP Archive Package (UAP)

Each package should contain:

-   Manifest
-   Decision Records
-   Knowledge Assets
-   Authorization Events
-   Evidence Snapshots
-   Governance References
-   Relationship Metadata
-   Audit History
-   Integrity Hashes
-   Schema Version

## Enterprise / MSP Support

USOP supports provider-neutral archive adapters such as Azure Blob
Storage, Amazon S3, Google Cloud Storage, S3-compatible storage, and
customer-managed repositories without changing Core.

## AI Principle

Future AI extensions reason over customer-owned knowledge. They never
become owners of that knowledge.

## USOP Trust Contract

USOP intentionally avoids vendor lock-in through proprietary storage.
Organizations remain customers because USOP continually increases the
value of their knowledge through relationships, workflows,
recommendations, and operational intelligence.

## Product Principle

> Customer knowledge is permanent.
>
> USOP intelligence is renewable.

USOP is the intelligence layer over customer-owned knowledge.
