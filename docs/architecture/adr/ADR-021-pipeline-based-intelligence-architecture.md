## ADR-021: Pipeline-Based Intelligence Architecture

# Status: Accepted

# Date: 2026-07-29

# Decision Owners: USOP Engineering

# Scope: Intelligence Architecture, Decision Intelligence, Platform Architecture

## Purpose

USOP exists to transform security operations from isolated technical activities into cumulative organizational intelligence.

As the platform evolves, intelligence capabilities will continue expanding across multiple domains, including identity, governance, organizational memory, decision drafting, threat intelligence, compliance, executive reporting, and future AI enhancements.

Although these capabilities consume different authoritative facts, they all share the same architectural objective:

Construct explainable intelligence that improves analyst effectiveness without replacing analyst judgment.

This Architecture Decision Record establishes the canonical architecture through which intelligence is constructed throughout USOP.

## Context

USOP has progressively evolved from independent security services into an integrated Security Decision Intelligence Platform.

Earlier architectural decisions established:

Relationship-First Architecture
Evolution Before Replacement
Organizational Memory
Canonical Decision Knowledge Relationships

These decisions successfully separated:

operational facts
organizational knowledge
accountable decisions
reusable relationships

The next stage of platform evolution introduces additional intelligence capabilities.

Without a governing architectural model, these capabilities naturally tend toward increasingly large intelligence engines responsible for:

gathering data
coordinating repositories
applying business rules
interpreting organizational meaning
assembling projections
presenting results

As these responsibilities accumulate, complexity grows faster than functionality.

Large intelligence engines become increasingly difficult to understand, validate, explain, and extend.

USOP therefore requires a repeatable architectural model that scales through composition rather than accumulation of responsibility.

## Problem Statement

Enterprise intelligence platforms frequently centralize multiple responsibilities into monolithic processing engines.

These engines often:

query numerous repositories
coordinate unrelated workflows
embed growing collections of business rules
accumulate feature-specific behavior
become difficult to test
become difficult to explain
become increasingly risky to modify

Over time, every new capability enlarges the same engine.

Eventually architectural complexity—not computational complexity—becomes the greatest long-term risk to platform evolution.

This outcome directly conflicts with USOP's architectural goals of:

explainability
deterministic behavior
maintainability
extensibility
analyst trust
long-term evolution

## Decision

USOP constructs intelligence through deterministic pipelines composed of independent builders.

Rather than concentrating intelligence inside large processing engines, intelligence shall be assembled from small, single-purpose builders operating on immutable, already-authoritative facts.

Each builder contributes one explainable portion of the final intelligence projection.

Pipelines coordinate builders.

Builders construct intelligence.

Repositories preserve facts.

Services perform business operations.

Presentation renders completed intelligence.

Each architectural layer owns one responsibility.

## Architectural Principles
# Principle 1 — Intelligence Is Constructed

USOP stores authoritative organizational facts.

Examples include:

identities
accounts
authorizations
recommendations
decisions
organizational guidance
governance policies
organizational patterns

These represent organizational truth.

Intelligence itself is never stored.

Instead, intelligence is constructed dynamically from the latest authoritative facts whenever requested.

This guarantees that intelligence always reflects current organizational knowledge while preserving a single operational source of truth.

# Principle 2 — Builders Consume Facts

Builders receive immutable context.

Builders never retrieve information.

Data acquisition remains the responsibility of repositories, domain services, and intelligence services before pipeline execution begins.

Builders shall never:

query repositories
open database sessions
invoke external APIs
modify persistence
initiate transactions
invoke generative AI

Builders exist solely to transform authoritative facts into explainable contributions.

# Principle 3 — One Builder Owns One Responsibility

Each builder owns one concern.

Examples include:

Recommendation Builder
History Builder
Guidance Builder
Pattern Builder
Threat Builder
Compliance Builder

Builders remain intentionally small.

Future capabilities should normally be implemented by adding another builder rather than enlarging existing builders.

# Principle 4 — Pipelines Orchestrate

Pipelines coordinate execution.

Pipelines are responsible for:

execution order
contribution collection
contract validation
projection construction

Pipelines intentionally do not contain business intelligence.

# Principle 5 — Every Contribution Must Be Explainable

Every sentence, recommendation, summary, metric, visualization, or decision draft produced by USOP must be traceable to authoritative evidence.

If supporting evidence cannot be identified, the contribution shall not be produced.

Explainability is an architectural requirement.

It is never optional.

# Principle 6 — Analysts Own Decisions

USOP prepares decisions.

Analysts make decisions.

USOP may:

organize evidence
summarize history
identify patterns
assemble documentation
prepare deterministic drafts

USOP shall never:

silently approve decisions
silently reject decisions
silently override organizational judgment
become the authoritative decision maker

Analysts remain accountable.

Organizations remain authoritative.

## Responsibilities
# Repository

Repositories preserve authoritative facts.

Repositories never construct intelligence.

# Service

Services own business operations.

Services validate workflow.

Services coordinate transactions.

Services never construct intelligence projections.

# Intelligence Service

Intelligence Services assemble authoritative facts.

Responsibilities include:

gathering scoped information
constructing immutable context
invoking pipelines
returning completed projections

Intelligence Services intentionally do not perform intelligence construction.

# Builder

Builders construct one explainable contribution.

Builders consume immutable facts.

Builders never coordinate with other builders.

Builders remain independently testable.

# Pipeline

Pipelines coordinate builders.

Pipelines preserve deterministic execution.

Pipelines assemble completed projections.

Pipelines intentionally remain unaware of repositories, presentation, and persistence.

## Canonical Pipeline
Authoritative Facts
        │
        ▼
Context Builder
        │
        ▼
Immutable Context
        │
        ▼
Pipeline
        │
        ├─────────────┐
        ▼             ▼
Recommendation   History
Builder          Builder
        ▼             ▼
Guidance      Pattern
Builder       Builder
        │             │
        └──────┬──────┘
               ▼
        Contributions
               │
               ▼
          Projection
               │
               ▼
              API
               │
               ▼
       User Interface

This architecture remains consistent regardless of the intelligence domain.

## AI Extension Model

Artificial Intelligence is an enhancement layer.

AI may improve:

readability
wording
summarization
presentation

AI shall not:

invent evidence
replace deterministic builders
bypass pipeline construction
become the authoritative source of organizational truth

Deterministic intelligence always precedes AI enhancement.

The deterministic projection remains authoritative.

## Architectural Benefits

This architecture:

reinforces KISS principles
enforces single responsibility
supports deterministic behavior
preserves explainability
enables independent testing
simplifies future extension
reduces regression risk
enables future commercial intelligence packs
supports local AI enhancement without architectural redesign

As USOP grows, intelligence expands horizontally through additional builders rather than vertically through increasingly complex engines.

## Trade-offs

This architecture introduces:

additional builder classes
additional orchestration
more explicit contracts
increased architectural discipline

These trade-offs are accepted because they significantly improve long-term maintainability, explainability, and platform evolution.

## Related ADRs
ADR-001 — Relationship-First Architecture
ADR-009 — Engine-First Architecture
ADR-017 — Evolution Before Replacement
ADR-018 — Canonical Relationship Model
ADR-019 — Organizational Memory and Evidence Architecture
ADR-020 — Canonical Decision Knowledge Relationships

## Summary

USOP constructs intelligence rather than storing it.

Facts remain authoritative.

Builders remain independent.

Pipelines construct intelligence.

Analysts remain accountable.

This architecture enables every future intelligence capability—including decision drafting, threat intelligence, compliance, executive reporting, CIAM, and future AI enhancement—to evolve through simple, deterministic builders composed into explainable intelligence pipelines.

USOP scales by adding independent capabilities rather than increasing architectural complexity.