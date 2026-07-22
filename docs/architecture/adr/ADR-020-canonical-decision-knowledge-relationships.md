# ADR-020: Canonical Decision Knowledge Relationships

**Status:** Accepted

**Date:** 2026-07-20

**Decision Owners:** USOP Engineering

**Scope:** Decision Intelligence, Organizational Memory, Knowledge Architecture

---

# Purpose

USOP exists to transform security operations from isolated technical activities
into cumulative organizational knowledge.

Security decisions represent accountable human judgment.

Organizational knowledge represents reusable experience.

Although these concepts are closely related, they serve fundamentally different
purposes and therefore require separate domain models connected through explicit
canonical relationships.

This architecture preserves historical accuracy while allowing organizational
knowledge to evolve independently.

---

# Context

Decision Records already preserve the operational context that existed when an
analyst made a security decision.

This includes:

- Evidence Snapshot
- Recommendation
- Risk Context
- Confidence
- Analyst Justification
- Approval
- Verification
- Outcome

Knowledge Assets preserve reusable organizational guidance.

Examples include:

- Operational procedures
- Security standards
- Investigation playbooks
- Lessons learned
- Organization-specific exceptions
- Platform guidance
- Reference material

Without an explicit relationship architecture, organizations would eventually
duplicate knowledge inside Decision Records, weaken historical auditability, and
limit future platform extensibility.

USOP therefore separates operational history from reusable organizational
knowledge.

---

# Problem Statement

Operational evidence answers:

"What happened?"

Decision Records answer:

"What did we decide?"

Knowledge Assets answer:

"What should future analysts know?"

These questions are intentionally different.

Embedding Organizational Knowledge inside Decision Records would create data
duplication, prevent controlled knowledge evolution, and reduce long-term
maintainability.

Conversely, allowing evolving Knowledge Assets to overwrite historical Decision
context would compromise auditability.

USOP requires an architecture that preserves both historical truth and evolving
organizational guidance.

---

# Decision

USOP introduces a canonical relationship between accountable security decisions
and reusable organizational knowledge.

```
DecisionRecord
        │
        ▼
DecisionKnowledge
        │
        ▼
KnowledgeAsset
```

DecisionKnowledge represents organizational meaning.

It does not duplicate Knowledge Assets.

It does not replace immutable Evidence Snapshots.

It exists solely to preserve the governed relationship between a historical
Decision Record and the Organizational Knowledge intentionally used to support
that decision.

---

# Architectural Principles

## Principle 1 — Facts Are Preserved in Immutable Snapshots

Operational evidence represents historical observations.

Evidence Snapshots preserve exactly what the analyst observed when the decision
was made.

Snapshots never evolve.

History never changes.

---

## Principle 2 — Relationships Express Meaning

Relationships communicate why domain objects are connected.

Meaning belongs inside canonical relationship models rather than duplicated
domain objects.

USOP favors explicit relationships over duplicated information.

---

## Principle 3 — Knowledge Evolves

Organizational guidance improves through operational experience.

Knowledge Assets may evolve through controlled versioning.

Historical Decision Records never change.

Decisions continue referencing the exact Knowledge Asset that informed the
decision at that point in time.

---

## Principle 4 — Producers May Change

Decision relationships remain independent of how knowledge is produced.

Knowledge may originate from:

- Security analysts
- Organization administrators
- Internal governance teams
- Future Knowledge Packs
- Future Intelligence Packs

Regardless of producer, DecisionKnowledge remains unchanged.

Only the producer changes.

This preserves architectural stability while allowing commercial capabilities
to expand without redesign.

---

# Responsibilities

## DecisionRecord

Decision Records own accountable human judgment.

Responsibilities include:

- Analyst accountability
- Operational workflow
- Evidence Snapshot
- Recommendation snapshot
- Approval lifecycle
- Verification lifecycle
- Review scheduling
- Outcome

Decision Records intentionally do not own reusable Organizational Knowledge.

---

## KnowledgeAsset

Knowledge Assets own reusable organizational experience.

Responsibilities include:

- Guidance
- Procedures
- Lessons learned
- Standards
- Exceptions
- Organizational references
- Version history

Knowledge Assets intentionally do not own operational decisions.

---

## DecisionKnowledge

DecisionKnowledge owns only the relationship between Decision Records and
Knowledge Assets.

Responsibilities include:

- Decision reference
- Knowledge reference
- Relationship classification
- Audit attribution

DecisionKnowledge intentionally contains no duplicated Knowledge content.

---

# Relationship Classification

The initial relationship vocabulary includes:

- PRIMARY_GUIDANCE
- SUPPORTING_GUIDANCE
- REFERENCE
- LESSONS_LEARNED
- EXCEPTION

Additional relationship classifications may be introduced through future
architectural decisions without redesigning the canonical relationship model.

---

# Commercial Architecture

USOP Core remains a complete professional security platform.

Core supports:

- Organizational Knowledge
- Decision governance
- Human accountability
- Canonical relationships

Commercial offerings extend knowledge production rather than altering core
architecture.

Examples include:

## Knowledge Packs

Knowledge Packs provide curated organizational guidance.

Examples:

- Internal SOP Libraries
- Security Standards
- Operational Procedures
- Vendor Hardening Guides
- DISA STIG Libraries
- CIS Benchmarks

## Intelligence Packs

Intelligence Packs continuously generate or enrich Organizational Knowledge.

Examples:

- CISA Known Exploited Vulnerabilities
- Vendor Security Advisories
- Threat Intelligence
- Vulnerability Prioritization
- Platform Security Recommendations

Knowledge Packs and Intelligence Packs create or enrich Knowledge Assets.

They never alter the canonical DecisionKnowledge relationship.

---

# Architectural Benefits

This architecture:

- preserves historical auditability
- prevents duplicated organizational guidance
- supports evolving knowledge through versioning
- reinforces Relationship-First Architecture
- enables future commercial capabilities without redesign
- maintains provider independence
- simplifies graph intelligence
- supports future Security Decision Intelligence

---

# Trade-offs

This architecture introduces an additional canonical relationship model.

Knowledge relationships require explicit governance.

Knowledge-producing components must conform to the canonical domain model.

These trade-offs are accepted because they significantly improve long-term
maintainability, extensibility, and architectural consistency.

---

# Related ADRs

- ADR-001 — Relationship-First Architecture
- ADR-008 — Continuous Evidence
- ADR-009 — Engine-First Architecture
- ADR-017 — Evolution Before Replacement
- ADR-018 — Canonical Relationship Model
- ADR-019 — Organizational Memory and Evidence Architecture

---

# Summary

USOP separates immutable operational facts from reusable organizational
knowledge.

Evidence preserves history.

Decision Records preserve accountable human judgment.

Knowledge Assets preserve reusable organizational experience.

DecisionKnowledge expresses the governed relationship between them.

Facts remain immutable.

Knowledge evolves.

Relationships preserve meaning.

This architecture enables USOP Core and future commercial Knowledge Packs and
Intelligence Packs to operate within one consistent, provider-independent,
relationship-first security platform.