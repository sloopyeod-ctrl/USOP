# USOP Engineering Development Workflow

## Purpose

This document defines the standard engineering workflow used to build and
evolve the Unified Security Operations Platform.

The objective is not merely to produce working software.

The objective is to continuously improve the product while preserving
architectural integrity, minimizing technical debt, protecting existing
capabilities, and advancing the long-term platform mission.

Every contributor should follow this workflow.

---

# Core Philosophy

USOP evolves before it replaces.

New capabilities should extend proven architecture whenever practical rather
than creating parallel implementations.

The platform should become easier to extend over time, not more complicated.

Every implementation should strengthen at least one of the following:

- Analyst effort
- Explainability
- Auditability
- Decision quality
- Scalability
- Organizational knowledge
- Architectural consistency

The first implementation idea is rarely the complete architectural solution.

Inspect first.

Challenge assumptions.

Then decide what should be built.

---

# Standard Engineering Lifecycle

Inspect
    â†“
Understand
    â†“
Challenge Assumptions
    â†“
Decide
    â†“
Implement
    â†“
Review
    â†“
Test
    â†“
Inspect the Exact Delta
    â†“
Commit
    â†“
Demonstrate

Skipping steps increases regression risk, duplicated responsibility, technical
debt, and future maintenance cost.

---

# Step 1 â€” Inspect

Before writing code, inspect the existing repository.

Review the relevant:

- Architecture
- ADRs
- Domain models
- Services
- Engines
- Pipelines
- Repositories
- APIs
- Schemas
- Frontend components
- Tests
- Configuration
- Documentation
- Current runtime behavior

Never assume a capability does not already exist.

Inspection should determine whether the requested capability is:

- Already implemented
- Partially implemented
- Implemented but not exposed
- Implemented through an obsolete path
- Missing entirely
- Better handled by extending an existing component

The first objective is to avoid duplicating work.

---

# Step 2 â€” Understand

Determine why the current implementation exists.

Identify:

- Its responsibilities
- Its architectural boundaries
- Its consumers
- Its dependencies
- Its test coverage
- Its compatibility requirements
- The ADRs governing it
- The product principle it supports

Do not replace working architecture without evidence that it cannot reasonably
evolve.

Understanding precedes design.

---

# Step 3 â€” Challenge Assumptions

Challenge the initial implementation idea before accepting it.

Ask:

- Does this capability already exist under another name?
- Is there already a rudimentary version that should evolve?
- Am I proposing another page, service, model, API, or engine unnecessarily?
- Would this create another source of truth?
- Would this duplicate business logic?
- Would this introduce a parallel execution path?
- Is the proposed component in the correct architectural layer?
- Is the requirement actually a presentation problem rather than a backend gap?
- Is the requirement actually an architectural gap rather than a UI feature?
- Would this design still make sense with five providers, domains, or customers?
- Is the platform being made simpler to extend or harder to understand?

The purpose of this step is not to delay implementation.

The purpose is to prevent avoidable rework.

---

# Step 4 â€” Decide

Choose the smallest architecturally complete approach.

The decision should identify:

- The canonical component to extend
- The responsibility being added
- The compatibility contract being preserved
- The tests required
- Whether documentation must change
- Whether an ADR is required

Create an ADR before implementation when the decision materially changes:

- Long-term architecture
- Ownership of business rules
- Persistence strategy
- Security boundaries
- Provider lifecycle
- Licensing behavior
- Canonical domain meaning
- Cross-domain relationships
- Platform-wide user experience principles

Do not create an ADR for routine implementation details that follow established
architecture.

---

# Step 5 â€” Implement

Implement one architectural responsibility at a time.

Prefer:

- Small vertical slices
- Existing services
- Existing engines
- Existing pipelines
- Existing provider contracts
- Existing canonical models
- Existing API families
- Existing frontend services
- Deterministic behavior
- Explicit naming
- Backward-compatible evolution

Avoid:

- Parallel subsystems
- Vendor-specific business logic in shared layers
- Business rules inside React
- Controllers that own orchestration
- Services that own domain meaning
- Frontend calculations that reinterpret backend intelligence
- Premature universal abstractions
- Unrelated cleanup inside a focused commit

A new abstraction should solve a demonstrated architectural need.

It should not be created solely because it may be useful someday.

---

# Step 6 â€” Review

Review the implementation before testing.

Evaluate product alignment, architectural alignment, and future extensibility.

Ask whether the implementation gives engineers time back, improves
understanding, supports accepted ADRs, remains provider-neutral, and will still
make sense as the platform grows.

---

# Step 7 â€” Test

Testing is required before every commit.

Use the smallest relevant test first, followed by the full regression surface:

Focused validation
    â†“
Subsystem regression
    â†“
Full applicable regression
    â†“
Runtime or browser validation

Testing may include:

- Unit tests
- Schema tests
- Service tests
- API contract tests
- OpenAPI tests
- Integration tests
- Database tests
- Frontend build
- Targeted frontend lint
- Browser validation
- Live provider validation when explicitly safe and required

Do not run live collection or synchronization merely to prove unrelated
structural changes.

Existing unrelated warnings should be recorded but should not be silently mixed
into the current implementation unless they block the release.

---

# Step 8 â€” Inspect the Exact Delta

Before committing, inspect exactly what changed.

Required checks normally include:

- git status --short
- git diff --check
- git diff --stat
- git diff

For staged work:

- git diff --cached --check
- git diff --cached --stat
- git diff --cached

Verify:

- Only intended files changed
- No unrelated files are staged
- No secrets or credentials are present
- No generated files were added unintentionally
- No duplicate implementation was introduced
- No compatibility contract changed accidentally
- No whitespace or encoding defects remain
- New files contain a final newline
- The commit represents one architectural responsibility

The Git delta is the final implementation contract.

Review it as carefully as the source code.

---

# Step 9 â€” Commit

Each commit should represent one architectural responsibility.

Commit messages should communicate architectural intent.

A focused commit is easier to review, test, revert, explain, audit, and include
in release notes.

---

# Step 10 â€” Demonstrate

Every completed capability should answer:

- What problem does this solve?
- What engineer effort does it remove?
- What uncertainty does it reduce?
- What decision does it improve?
- How is it explained to a beta user?
- How does it support the 10â€“20 second operational scan?
- How does it strengthen the product rather than merely add code?

If a capability cannot be explained or demonstrated, reconsider whether it
belongs in the current release.

---

# Inspect Before Implement Checklist

Before implementation, answer:

- What existing capability was inspected?
- Which ADRs govern this area?
- Does the requested capability already exist in whole or in part?
- Is there a rudimentary implementation that should evolve?
- What is the canonical architectural path?
- Would this create another source of truth?
- Would this duplicate business logic?
- Would this introduce a parallel execution path?
- What compatibility contract must remain stable?
- Is a new abstraction truly required?
- Is an ADR required?
- What focused tests protect the change?
- What full regression surface must remain green?
- How will the exact Git delta be reviewed?
- How does this improve the engineer or analyst experience?

Implementation should not begin until these questions can be answered with
reasonable confidence.

---

# Engineering Layer Responsibilities

## Backend

The backend owns business rules, security meaning, canonical relationships,
recommendations, confidence, governance, validation, orchestration, persistence
decisions, and audit behavior.

## Frontend

The frontend owns presentation, visual hierarchy, progressive disclosure, user
interaction, workflow coordination, and rendering prepared intelligence.

React must not become a second source of business truth.

## Controllers

Controllers translate transport requests and responses. They remain thin.

## Services

Services coordinate workflows. They do not redefine canonical domain meaning.

## Models and Repositories

Models own persistence structure. Repositories own persistence access.

## Builders and Pipelines

Builders construct deterministic intelligence. Pipelines compose independent
builders.

## Providers

Providers retrieve and normalize facts from authoritative systems. Providers do
not redefine the authority of those systems.

---

# Definition of Done

A capability is complete when:

- The implementation is complete
- Applicable ADRs and standards are followed
- Focused tests pass
- Full applicable regression tests pass
- Runtime or browser behavior is verified when relevant
- The exact Git delta is reviewed
- Whitespace and encoding checks pass
- Documentation is updated when required
- The commit contains one architectural responsibility
- The product benefit can be demonstrated
- The repository is clean except for intentionally excluded files

Only then should the change be committed and pushed.

---

# Continuous Improvement

This workflow may evolve as USOP grows.

Changes should simplify engineering, improve confidence, or strengthen
architectural integrity.

The workflow must not become process for its own sake.

---

# Final Principle

Inspect before implementing.

Understand before replacing.

Challenge assumptions before designing.

Extend before duplicating.

Test before committing.

Review the exact delta before trusting it.

Build the smallest complete capability that strengthens the platform.
